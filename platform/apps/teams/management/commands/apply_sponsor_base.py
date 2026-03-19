from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.teams.models import Sponsor
from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType


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

                team.credits = (team.credits or 0) + amount
                team.save(update_fields=["credits"])
                CreditTransaction.objects.create(
                    team=team,
                    amount=amount,
                    transaction_type=TransactionType.SPONSOR_BASE,
                    description=f"Sponsor base bonus {sponsor.name} ({marker})",
                )
                applied += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Applied sponsor base bonus: {applied}; skipped: {skipped}"
            )
        )
