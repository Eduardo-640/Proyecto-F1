from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.races.models import Race, RaceResult
from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType
from apps.teams.models import SponsorPayout

# Fraction of remaining payout applied per race (before performance modifier)
PAYOUT_RATE_PER_RACE = 0.25


class Command(BaseCommand):
    help = "Settle sponsor pending payouts for a race based on results (performance)."

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=int, help="Race id to settle payouts for")

    def handle(self, *args, **options):
        race_id = options.get("race_id")
        try:
            race = Race.objects.get(pk=int(race_id))
        except Race.DoesNotExist:
            raise CommandError(f"Race id {race_id} not found")

        results_qs = RaceResult.objects.filter(race=race)
        if not results_qs.exists():
            self.stdout.write(
                self.style.NOTICE(f"No results for race {race}; nothing to settle.")
            )
            return

        # compute team points in this race
        team_points = {}
        for rr in results_qs:
            team = rr.team
            team_points[team.id] = team_points.get(team.id, 0) + (
                rr.points_awarded or 0
            )

        if not team_points:
            self.stdout.write(
                self.style.NOTICE("No points awarded in this race — no payouts.")
            )
            return

        max_points = max(team_points.values())
        if max_points <= 0:
            self.stdout.write(
                self.style.NOTICE("Max points is zero — no performance-based payouts.")
            )
            return

        applied = 0
        skipped = 0
        with transaction.atomic():
            # find payouts for teams that have entries in this race and remaining > 0 in same season
            payouts = SponsorPayout.objects.filter(
                remaining_amount__gt=0,
                team__in=[t for t in team_points.keys()],
                season=race.season,
            )
            for p in payouts:
                team_id = p.team.id
                points = team_points.get(team_id, 0)
                if points <= 0:
                    skipped += 1
                    continue

                perf = float(points) / float(max_points)
                pay = int(round(p.remaining_amount * PAYOUT_RATE_PER_RACE * perf))
                if pay <= 0:
                    skipped += 1
                    continue

                marker = f"sponsor_payout:race:{race.id}:payout:{p.id}"
                exists = CreditTransaction.objects.filter(
                    team=p.team,
                    transaction_type=TransactionType.SPONSOR_PAYOUT,
                    description__contains=marker,
                ).exists()
                if exists:
                    skipped += 1
                    continue

                # apply payment
                p.remaining_amount = max(0, p.remaining_amount - pay)
                p.save(update_fields=["remaining_amount"])  # persist remainder

                CreditTransaction.objects.create(
                    team=p.team,
                    amount=pay,
                    transaction_type=TransactionType.SPONSOR_PAYOUT,
                    description=f"Sponsor payout {p.sponsor.name} ({marker})",
                    race=race,
                )
                applied += 1

        self.stdout.write(self.style.SUCCESS(f"Applied: {applied}; skipped: {skipped}"))
