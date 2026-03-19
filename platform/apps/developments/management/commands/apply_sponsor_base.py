from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.seasons.models import Season
from apps.teams.models import Sponsor
from apps.races.models import CreditTransaction


class Command(BaseCommand):
    help = "Apply sponsor base bonuses for a season (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "season", type=int, help="Season id to apply sponsor base bonuses"
        )

    def handle(self, *args, **options):
        season_id = options.get("season")
        try:
            season = Season.objects.get(id=season_id)
        except Season.DoesNotExist:
            raise CommandError(f"Season id={season_id} not found")

        applied = 0
        skipped = 0

        # Process sponsors that are assigned to teams only (team FK not null)
        sponsors = Sponsor.objects.filter(
            team__isnull=False, active=True
        ).select_related("team")

        for sponsor in sponsors:
            marker = f"season:{season_id}|sponsor:{sponsor.pk}"
            # Idempotency: check existing CreditTransaction with this marker
            exists = CreditTransaction.objects.filter(
                team=sponsor.team,
                transaction_type=CreditTransaction._meta.get_field(
                    "transaction_type"
                ).choices
                and "sponsor_base",
                description__contains=marker,
            ).exists()

            if exists:
                skipped += 1
                self.stdout.write(
                    f"Skipping sponsor {sponsor} for {sponsor.team} (already applied)"
                )
                continue

            if sponsor.base_bonus <= 0:
                skipped += 1
                self.stdout.write(f"Skipping sponsor {sponsor} (no base_bonus)")
                continue

            # Atomic update per sponsor to avoid partial application
            try:
                with transaction.atomic():
                    team = sponsor.team
                    team.credits = team.credits + sponsor.base_bonus
                    team.save(update_fields=["credits"])

                    CreditTransaction.objects.create(
                        team=team,
                        amount=sponsor.base_bonus,
                        transaction_type="sponsor_base",
                        description=f"Sponsor base bonus: {sponsor.name} ({marker})",
                    )
                applied += 1
                self.stdout.write(
                    f"Applied {sponsor.base_bonus} to {team} from sponsor {sponsor}"
                )
            except Exception as e:
                self.stderr.write(
                    f"Error applying sponsor {sponsor} to {sponsor.team}: {e}"
                )

        self.stdout.write(f"Done. applied={applied}, skipped={skipped}")
