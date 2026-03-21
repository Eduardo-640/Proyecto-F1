from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.races.models import Race, RaceResult, CreditTransaction
from apps.races.constants import TransactionType
from apps.drivers.models import DriverStanding, DriverPointTransaction
from apps.teams.models import Team, SponsorPayout


class Command(BaseCommand):
    help = "Rollback race results: revert credit and point transactions and recompute standings."

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=int, help="Race id to rollback")

    def handle(self, *args, **options):
        race_id = options.get("race_id")
        try:
            race = Race.objects.get(pk=int(race_id))
        except Race.DoesNotExist:
            raise CommandError(f"Race id {race_id} not found")

        # Gather transactions to revert
        txs = CreditTransaction.objects.filter(race=race)
        if not txs.exists():
            self.stdout.write(
                self.style.NOTICE("No credit transactions for this race.")
            )

        with transaction.atomic():
            # Revert credit transactions
            for tx in txs:
                team = tx.team
                amt = tx.amount or 0
                # Subtract the amount, avoiding negative balances
                new_credits = max(0, (team.credits or 0) - amt)
                team.credits = new_credits
                team.save(update_fields=["credits"])

                # If this was a sponsor payout, try to restore SponsorPayout.remaining_amount
                if (
                    tx.transaction_type == TransactionType.SPONSOR_PAYOUT
                    and tx.description
                ):
                    # look for marker 'sponsor_payout:race:<race_id>:payout:<payout_id>'
                    parts = tx.description.split("sponsor_payout:race:")
                    if len(parts) > 1:
                        try:
                            tail = parts[1]
                            # tail format: '<raceid>:payout:<payoutid>' inside parentheses maybe
                            # extract payout id by splitting
                            if ":payout:" in tail:
                                payout_part = tail.split(":payout:")[-1]
                                # strip non-digits
                                payout_id = int(
                                    "".join(c for c in payout_part if c.isdigit())
                                )
                                p = SponsorPayout.objects.filter(pk=payout_id).first()
                                if p:
                                    p.remaining_amount = min(
                                        p.total_amount, p.remaining_amount + amt
                                    )
                                    p.save(update_fields=["remaining_amount"])
                        except Exception:
                            # ignore parsing errors
                            pass

                # delete the transaction record
                tx.delete()

            # Revert driver point transactions for this race
            pt_txs = DriverPointTransaction.objects.filter(race=race)
            for pt in pt_txs:
                driver = pt.driver
                ds = DriverStanding.objects.filter(
                    driver=driver, season=race.season
                ).first()
                if ds:
                    ds.total_points = max(0, ds.total_points - (pt.amount or 0))
                    # We will fully recompute aggregate fields below, so leave counts minimal here
                    ds.save(update_fields=["total_points"])
                pt.delete()

            # Remove RaceResult rows for this race
            RaceResult.objects.filter(race=race).delete()

            # Recompute DriverStanding aggregates from remaining RaceResult rows for the season
            standings = DriverStanding.objects.filter(season=race.season)
            for ds in standings:
                # reset aggregates
                ds.total_points = 0
                ds.races_entered = 0
                ds.wins = 0
                ds.podiums = 0
                ds.pole_positions = 0
                ds.fastest_laps = 0
                ds.dnf_count = 0
                ds.save()

            # Rebuild from scratch
            rr_qs = RaceResult.objects.filter(race__season=race.season)
            for rr in rr_qs:
                try:
                    ds, _ = DriverStanding.objects.get_or_create(
                        driver=rr.driver, season=rr.race.season
                    )
                    ds.total_points += rr.points_awarded or 0
                    if rr.finished_race:
                        ds.races_entered += 1
                    if rr.position == 1:
                        ds.wins += 1
                    if rr.position and 1 <= rr.position <= 3:
                        ds.podiums += 1
                    if rr.pole_position:
                        ds.pole_positions += 1
                    if rr.fastest_lap:
                        ds.fastest_laps += 1
                    if not rr.finished_race:
                        ds.dnf_count += 1
                    ds.save()
                except Exception:
                    continue

        self.stdout.write(
            self.style.SUCCESS(
                f"Rollback completed for race {race} (transactions reverted)."
            )
        )
