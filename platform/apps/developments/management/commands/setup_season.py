from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from apps.seasons.models import Season
from apps.developments.models import AccionMasiva


class Command(BaseCommand):
    help = (
        "Automate season setup: optionally load sponsor fixtures, apply sponsor base bonuses, "
        "and generate initial presets for all teams in a season."
    )

    def add_arguments(self, parser):
        parser.add_argument("season", type=int, help="Season id to initialise")
        parser.add_argument(
            "--load-sponsors",
            action="store_true",
            help="Load the sponsors fixture before applying bonuses",
        )

    def handle(self, *args, **options):
        season_id = options.get("season")
        load_sponsors = options.get("load_sponsors")

        try:
            season = Season.objects.get(id=season_id)
        except Season.DoesNotExist:
            raise CommandError(f"Season id={season_id} not found")

        # Locate fixture path relative to this file: platform/apps/teams/fixtures
        fixture_path = (
            Path(__file__).resolve().parents[4]
            / "apps"
            / "teams"
            / "fixtures"
            / "sponsors_template.json"
        )

        if load_sponsors:
            if not fixture_path.exists():
                raise CommandError(f"Fixture not found: {fixture_path}")
            self.stdout.write(f"Loading sponsors fixture: {fixture_path}")
            call_command("loaddata", str(fixture_path))

            # Validate sponsor categories and attempt to fix common aliases
            self.stdout.write(
                "Validating sponsors (running validate_sponsors --fix)..."
            )
            try:
                call_command("validate_sponsors", "--fix")
                self.stdout.write("Sponsor validation complete.")
            except Exception as e:
                # Non-fatal: warn and continue
                self.stdout.write(f"Warning: validate_sponsors failed: {e}")

        self.stdout.write(f"Applying sponsor base bonuses for season {season_id}")
        call_command("apply_sponsor_base", str(season_id))

        self.stdout.write(
            "Creating AccionMasiva to generate initial presets (init_presets)"
        )
        accion = AccionMasiva.objects.create(
            action_type=AccionMasiva.ActionType.INIT_PRESETS, season=season
        )

        # AccionMasiva.execute() runs on create; show result
        self.stdout.write(f"AccionMasiva status: {accion.status}")
        self.stdout.write("Result log:\n")
        self.stdout.write(accion.result_log or "(no output)")
