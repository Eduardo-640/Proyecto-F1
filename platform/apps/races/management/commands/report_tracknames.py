import json
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Scans media/input JSON files and reports unique TrackName values"

    def add_arguments(self, parser):
        parser.add_argument(
            "--input-dir", help="Path to media input folder", default=None
        )

    def handle(self, *args, **options):
        input_dir = options.get("input_dir")
        if not input_dir:
            # default relative locations
            candidates = [
                Path.cwd() / "media" / "input",
                Path.cwd().parent / "media" / "input",
                Path.cwd().parent.parent / "media" / "input",
            ]
        else:
            candidates = [Path(input_dir)]

        # prefer an existing input dir that contains JSONs
        found = None
        for c in candidates:
            if c.exists() and any(c.glob("*.json")):
                found = c
                break

        if not found:
            # fallback to first existing input dir (even if empty)
            for c in candidates:
                if c.exists():
                    found = c
                    break

        if not found:
            self.stdout.write(
                self.style.ERROR(f"No media/input found among candidates: {candidates}")
            )
            return

        tracknames = {}
        for f in sorted(found.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                tn = data.get("TrackName") or data.get("Track") or None
                tracknames.setdefault(tn, []).append(f.name)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed reading {f.name}: {e}"))

        self.stdout.write(f"Found {len(tracknames)} distinct TrackName values:")
        for tn, files in tracknames.items():
            self.stdout.write(f"- {repr(tn)}: {len(files)} files -> {files[:5]}")
