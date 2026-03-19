"""
Management command: apply_season_bonuses

Applies sponsor-affinity starting level bonuses to all TeamDevelopment
entries in a season that have an eligible main sponsor.

Run this BEFORE init_season_setups so the initial preset already reflects
the boosted levels.

Usage
-----
    python manage.py apply_season_bonuses <season_id>
    python manage.py apply_season_bonuses <season_id> --dry-run
"""

from django.core.management.base import BaseCommand, CommandError

from apps.developments.models import TeamDevelopment
from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType as RaceTransactionType
from apps.developments.setup_service import (
    apply_starting_bonuses,
    get_starting_department_bonus,
)
from apps.seasons.models import Season


class Command(BaseCommand):
    help = "Apply sponsor affinity starting bonuses to all teams in a season."

    def add_arguments(self, parser):
        parser.add_argument("season_id", type=int, help="PK of the target Season.")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be applied without touching the database.",
        )

    def handle(self, *args, **options):
        season_id = options["season_id"]
        dry_run = options["dry_run"]

        try:
            season = Season.objects.get(pk=season_id)
        except Season.DoesNotExist:
            raise CommandError(f"Season with id={season_id} does not exist.")

        devs = TeamDevelopment.objects.filter(season=season).select_related(
            "team", "season"
        )
        if not devs.exists():
            raise CommandError(
                f"No TeamDevelopment entries for season '{season}'. Create them first."
            )

        applied = none_found = 0
        for dev in devs:
            bonuses = get_starting_department_bonus(dev.team)
            if not bonuses:
                self.stdout.write(f"  SKIP  {dev.team} — no sponsor affinity bonus")
                none_found += 1
                continue

            # Format bonus string showing signs for positive/negative
            # Compute intended/clamped deltas for readable output
            max_level = 5
            min_level = 1
            intended = {}
            for dept, raw in bonuses.items():
                current = dev.get_level(dept)
                new_level = max(min_level, min(current + raw, max_level))
                delta = new_level - current
                if delta != 0:
                    intended[dept] = delta

            bonus_str = (
                ", ".join(f"{d} {('+' if v>0 else '')}{v}" for d, v in intended.items())
                or "(no net change)"
            )

            if dry_run:
                self.stdout.write(f"  DRY   {dev.team} → {bonus_str}")
                applied += 1
                continue

            applied_bonuses = apply_starting_bonuses(dev)
            if applied_bonuses:
                # record an audit transaction (amount 0)
                CreditTransaction.objects.create(
                    team=dev.team,
                    amount=0,
                    transaction_type=RaceTransactionType.ADMIN_ADJUSTMENT,
                    description=(
                        f"Starting bonuses applied: {', '.join(sorted([f'{k}{v:+d}' for k,v in applied_bonuses.items()]))} "
                        f"(sponsor={getattr(dev.team.sponsors.filter(is_main=True).first(), 'name', 'None')}, season={season})"
                    ),
                )

            self.stdout.write(self.style.SUCCESS(f"  OK    {dev.team} → {bonus_str}"))
            applied += 1

        label = "Would apply" if dry_run else "Applied"
        self.stdout.write(
            self.style.SUCCESS(
                f"\n{label} bonuses to {applied} team(s). "
                f"{none_found} had no applicable affinity."
            )
        )
