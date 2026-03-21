from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.teams.models import Sponsor
from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType
from apps.teams.models import SponsorPayout

# Configuration: fraction of base_bonus applied immediately and an absolute cap
UPFRONT_PERCENT = 0.25  # 25% upfront
UPFRONT_CAP = 2000  # maximum immediate grant per sponsor


class Command(BaseCommand):
    help = "Apply Sponsor.base_bonus to each team's credits for a given season (season id required)"

    def add_arguments(self, parser):
        parser.add_argument("season", type=int, help="Season id to apply bonuses for")

    def handle(self, *args, **options):
        season_id = options.get("season")
        if not season_id:
            raise CommandError("Provide a season id")

        applied = 0
        skipped = 0
        with transaction.atomic():
            for sponsor in Sponsor.objects.filter(active=True).select_related("team"):
                if not sponsor.team:
                    skipped += 1
                    continue
                team = sponsor.team
                amount = sponsor.base_bonus or 0
                if amount == 0:
                    skipped += 1
                    continue

                # Prevent duplicate application: look for existing CreditTransaction with marker
                marker = f"sponsor_base:season:{season_id}:sponsor:{sponsor.id}"
                exists = CreditTransaction.objects.filter(
                    team=team,
                    transaction_type=TransactionType.SPONSOR_BASE,
                    description__contains=marker,
                ).exists()
                if exists:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"Skipping {team}: sponsor {sponsor} already applied for season {season_id}"
                        )
                    )
                    skipped += 1
                    continue

                # Split into upfront + scheduled remainder to avoid big early advantages
                upfront = int(round((amount or 0) * UPFRONT_PERCENT))
                upfront = min(upfront, UPFRONT_CAP)
                remainder = (amount or 0) - upfront

                if upfront > 0:
                    team.credits = (team.credits or 0) + upfront
                    team.save(update_fields=["credits"])
                    CreditTransaction.objects.create(
                        team=team,
                        amount=upfront,
                        transaction_type=TransactionType.SPONSOR_BASE,
                        description=f"Sponsor upfront {sponsor.name} ({marker})",
                    )

                if remainder > 0:
                    # Record a scheduled payout to be applied later (e.g., on race results)
                    SponsorPayout.objects.create(
                        sponsor=sponsor,
                        team=team,
                        season_id=season_id,
                        total_amount=amount,
                        remaining_amount=remainder,
                    )
                applied += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Applied sponsor base bonus: {applied}; skipped: {skipped}"
            )
        )
