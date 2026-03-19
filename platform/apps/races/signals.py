from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import transaction

from .models import RaceResult, Race, CreditTransaction
from apps.drivers.models import DriverStanding
from apps.teams.models import Team
from apps.races.constants import TransactionType


@receiver(pre_delete, sender=Race)
def revert_race_effects(sender, instance: Race, **kwargs):
    """When a Race is deleted, revert DriverStanding and Team credits based on existing RaceResults.

    This runs in a transaction to ensure consistency.
    """
    with transaction.atomic():
        results = list(
            RaceResult.objects.filter(race=instance).select_related("driver", "team")
        )
        for rr in results:
            team = rr.team
            driver = rr.driver
            season = instance.season

            # Reverse DriverStanding effects
            ds = DriverStanding.objects.filter(driver=driver, season=season).first()
            if ds:
                pts = rr.points_awarded or 0
                ds.total_points = max(0, ds.total_points - pts)

                if rr.finished_race:
                    ds.races_entered = max(0, ds.races_entered - 1)
                else:
                    # was DNF, reduce DNF count
                    ds.dnf_count = max(0, ds.dnf_count - 1)

                if rr.position == 1:
                    ds.wins = max(0, ds.wins - 1)

                if rr.position and 1 <= rr.position <= 3:
                    ds.podiums = max(0, ds.podiums - 1)

                if rr.pole_position:
                    ds.pole_positions = max(0, ds.pole_positions - 1)

                if rr.fastest_lap:
                    ds.fastest_laps = max(0, ds.fastest_laps - 1)

                ds.save()

            # Reverse Team credits: assume 10 credits per point (same multiplier used when awarding)
            pts = rr.points_awarded or 0
            credit_delta = -(pts * 10)
            if credit_delta != 0 and team is not None:
                team.credits = max(0, (team.credits or 0) + credit_delta)
                team.save()
                CreditTransaction.objects.create(
                    team=team,
                    amount=credit_delta,
                    transaction_type=TransactionType.ADMIN_ADJUSTMENT,
                    description=f"Reversal for deleted race {instance.id}",
                    race=instance,
                )

        # Optionally delete the RaceResult rows now; they will be cascaded when the Race is deleted,
        # but removing them here makes the reversal explicit.
        RaceResult.objects.filter(race=instance).delete()
