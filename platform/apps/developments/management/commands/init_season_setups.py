"""
Management command: init_season_setups

Creates the initial car setup snapshot (version 1) for every team that has
a ``TeamDevelopment`` entry in the given season and does not yet have a
snapshot.

Usage
-----
    python manage.py init_season_setups <season_id>
    python manage.py init_season_setups <season_id> --bias speed
    python manage.py init_season_setups <season_id> --bias random   (default)
    python manage.py init_season_setups <season_id> --bias balanced --dry-run

Options
-------
--bias      Force a specific preset bias for every team.
            Omit (or use "random") to assign a different random bias per team.
--dry-run   Print what would happen without writing to the database.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.developments import setup_generator as sg
from apps.developments.models import CarSetupSnapshot, TeamDevelopment
from apps.developments.setup_service import generate_initial_preset
from apps.seasons.models import Season


class Command(BaseCommand):
    help = "Generate initial setup presets for all teams in a season."

    def add_arguments(self, parser):
        parser.add_argument("season_id", type=int, help="PK of the target Season.")
        parser.add_argument(
            "--bias",
            default="random",
            choices=list(sg.PRESET_BIASES.keys()) + ["random"],
            help=(
                "Preset bias to assign. "
                "'random' (default) picks a different one per team."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without touching the database.",
        )

    def handle(self, *args, **options):
        season_id = options["season_id"]
        bias_opt = options["bias"]
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
                f"No TeamDevelopment entries found for season '{season}'. "
                "Create them first via the admin or a fixture."
            )

        existing = set(
            CarSetupSnapshot.objects.filter(season=season).values_list(
                "team_id", flat=True
            )
        )

        created = 0
        skipped = 0

        for dev in devs:
            if dev.team_id in existing:
                self.stdout.write(
                    self.style.WARNING(f"  SKIP  {dev.team} — snapshot already exists")
                )
                skipped += 1
                continue

            bias = (
                bias_opt
                if bias_opt != "random"
                else __import__("random").choice(list(sg.PRESET_BIASES.keys()))
            )

            if dry_run:
                self.stdout.write(f"  DRY   {dev.team} → bias={bias}")
                created += 1
                continue

            try:
                with transaction.atomic():
                    snapshot = generate_initial_preset(dev, bias=bias)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  OK    {dev.team} → bias={snapshot.preset_bias} "
                        f"(v{snapshot.version})"
                    )
                )
                created += 1
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"  ERROR {dev.team}: {exc}"))

        label = "Would create" if dry_run else "Created"
        self.stdout.write(
            self.style.SUCCESS(f"\n{label} {created} snapshot(s), skipped {skipped}.")
        )
