import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import transaction

from apps.teams.models import Team
from apps.races.models import RaceResult, Race, CreditTransaction
from apps.drivers.models import Driver, DriverStanding


def find_media_dirs():
    # prefer MEDIA_ROOT
    if getattr(settings, "MEDIA_ROOT", None):
        media_root = Path(settings.MEDIA_ROOT)
        return media_root / "input", media_root / "output"

    cwd = Path.cwd()
    candidates = [cwd, cwd.parent, cwd.parent.parent, cwd.parent.parent.parent]
    for p in candidates:
        inp = p / "media" / "input"
        out = p / "media" / "output"
        if out.exists() or inp.exists():
            inp.mkdir(parents=True, exist_ok=True)
            out.mkdir(parents=True, exist_ok=True)
            return inp, out

    # fallback
    inp = cwd / "media" / "input"
    out = cwd / "media" / "output"
    inp.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    return inp, out


class Command(BaseCommand):
    help = "Delete teams, races and standings; recreate team per driver; move JSONs from output->input and rescan. IRREVERSIBLE."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-scan", action="store_true", help="Do not run the scanner after reset"
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "*** About to DELETE Teams, Races, RaceResults, DriverStandings and CreditTransactions. This is irreversible. ***"
            )
        )
        confirm = input("Type 'yes' to continue: ")
        if confirm.strip().lower() != "yes":
            self.stdout.write("Aborted by user.")
            return

        inp, out = find_media_dirs()
        self.stdout.write(f"Using media input: {inp} and output: {out}")

        with transaction.atomic():
            # delete race-related data
            RaceResult.objects.all().delete()
            DriverStanding.objects.all().delete()
            CreditTransaction.objects.all().delete()
            Race.objects.all().delete()

            # delete teams
            Team.objects.all().delete()

            # recreate per-driver teams
            created = 0
            for d in Driver.objects.all():
                name = d.name or "Unnamed"
                base = f"{name} - Team"
                candidate = base
                suffix = 1
                while Team.objects.filter(name__iexact=candidate).exists():
                    suffix += 1
                    candidate = f"{base} {suffix}"
                t = Team.objects.create(name=candidate)
                d.team = t
                d.save(update_fields=["team"])
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted data and created {created} teams (one per driver)."
            )
        )

        # move files from output back to input
        moved = 0
        for f in list(out.glob("*.json")):
            dst = inp / f.name
            shutil.move(str(f), str(dst))
            moved += 1
        self.stdout.write(
            self.style.SUCCESS(f"Moved {moved} files from output -> input")
        )

        if not options.get("no_scan"):
            self.stdout.write("Running scanner (process_input_folder)...")
            call_command("process_input_folder")
            self.stdout.write(self.style.SUCCESS("Scanner finished."))
