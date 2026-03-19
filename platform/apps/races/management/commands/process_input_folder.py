import json
import shutil
import re
from pathlib import Path
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.races.management.commands.process_results import (
    Command as ProcessResultsCommand,
)
from apps.races.models import Race, Circuit
from apps.seasons.models import Season
from django.db.models import Max


def get_input_output_dirs():
    """Return (input_dir, output_dir). Prefer settings.MEDIA_ROOT if available,
    otherwise search upward from cwd for a media/input directory.
    """
    # Prefer MEDIA_ROOT/input
    if getattr(settings, "MEDIA_ROOT", None):
        media_root = Path(settings.MEDIA_ROOT)
        input_dir = media_root / "input"
        output_dir = media_root / "output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        return input_dir, output_dir

    # fallback: search cwd and up to 4 parents
    cwd = Path.cwd()
    candidates = [
        cwd,
        cwd.parent,
        cwd.parent.parent,
        cwd.parent.parent.parent,
        cwd.parent.parent.parent.parent,
    ]

    # Prefer an existing media/input that contains JSON files
    for p in candidates:
        candidate = p / "media" / "input"
        if candidate.exists() and any(candidate.glob("*.json")):
            out = candidate.parent / "output"
            out.mkdir(parents=True, exist_ok=True)
            return candidate, out

    # If none contain files, return the first existing media/input (even if empty)
    for p in candidates:
        candidate = p / "media" / "input"
        if candidate.exists():
            out = candidate.parent / "output"
            out.mkdir(parents=True, exist_ok=True)
            return candidate, out

    # last resort: create media/input in cwd
    input_dir = cwd / "media" / "input"
    output_dir = cwd / "media" / "output"
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    return input_dir, output_dir


def infer_race_from_filename(name: str):
    base = Path(name).stem
    m = re.match(
        r"^(?P<season>\d{4})[_-](?P<round>\d{1,2})[_-](?P<type>practice|qualify|qualifying|race)$",
        base,
        re.I,
    )
    if m:
        return {
            "season": int(m.group("season")),
            "round": int(m.group("round")),
            "type": m.group("type").lower(),
        }

    m2 = re.match(
        r"^(?P<year>\d{4})[_-](?P<mon>\d{1,2})[_-](?P<day>\d{1,2})[_-](?P<h>\d{1,2})[_-](?P<m>\d{1,2})[_-]?(?P<type>practice|qualify|qualifying|race)$",
        base,
        re.I,
    )
    if m2:
        dt = datetime(
            int(m2.group("year")),
            int(m2.group("mon")),
            int(m2.group("day")),
            int(m2.group("h")),
            int(m2.group("m")),
        )
        return {"datetime": dt, "type": m2.group("type").lower()}

    return {}


class Command(BaseCommand):
    help = "Process all JSON files in media/input using process_results and move them to media/output after processing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only list files and inferred targets without moving files",
        )

    def handle(self, *args, **options):
        input_dir, output_dir = get_input_output_dirs()
        # create discarded directory next to output
        discarded_dir = output_dir.parent / "discarded"
        discarded_dir.mkdir(parents=True, exist_ok=True)

        files = list(input_dir.glob("*.json"))
        if not files:
            self.stdout.write("No JSON files found in media/input")
            return

        pr = ProcessResultsCommand()

        for f in files:
            info = infer_race_from_filename(f.name)
            self.stdout.write(f"Processing {f.name} -> filename inference: {info}")

            # Try to open JSON and infer by TrackName
            race = None
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                track = data.get("TrackName") or data.get("Track") or None

                # find circuit by Assetto name or by partial match
                circuit = None
                if track:
                    circuit = Circuit.objects.filter(assetto_name__iexact=track).first()
                    if not circuit:
                        circuit = Circuit.objects.filter(name__icontains=track).first()
                    if not circuit:
                        circuit = Circuit.objects.filter(
                            assetto_name__icontains=track
                        ).first()

                # determine desired session status from filename/JSON if available
                session = info.get("type") or (data.get("Type") or "").strip().lower()
                if session in ("qualify", "qualifying"):
                    session_status = "qualifying"
                elif session == "race":
                    session_status = "race"
                else:
                    session_status = "practice"

                if circuit:
                    # Prefer an existing race matching circuit + status
                    race = (
                        Race.objects.filter(circuit=circuit, status=session_status)
                        .order_by("-race_date", "-round_number")
                        .first()
                    )
                    if race:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Inferred race {race.id} from TrackName '{track}' (circuit {circuit})"
                            )
                        )
                    else:
                        # no existing race for this circuit+status — consider creating one if we have datetime
                        if info.get("datetime"):
                            target_date = info.get("datetime").date()
                            # determine season by date (strict). If multiple seasons
                            # cover the same date we treat it as ambiguous and skip
                            # to avoid assigning races to the wrong season.
                            seasons_for_date = list(
                                Season.objects.filter(
                                    start_date__lte=target_date,
                                    end_date__gte=target_date,
                                )
                            )
                            if len(seasons_for_date) == 1:
                                season = seasons_for_date[0]
                            else:
                                # strict mode: if the date is not covered by exactly one
                                # season we consider it ambiguous and skip processing
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"No single season covers {target_date}; skipping {f.name} to avoid incorrect assignment."
                                    )
                                )
                                season = None

                            # determine round number: try to reuse existing round on same date/circuit, else next
                            if season:
                                existing = (
                                    Race.objects.filter(
                                        season=season,
                                        circuit=circuit,
                                        race_date=target_date,
                                    )
                                    .order_by("-round_number")
                                    .first()
                                )
                                if existing:
                                    round_number = existing.round_number
                                else:
                                    max_round = (
                                        Race.objects.filter(season=season).aggregate(
                                            Max("round_number")
                                        )["round_number__max"]
                                    ) or 0
                                    round_number = max_round + 1
                            else:
                                # no season determined (strict mode) -> move to discarded and skip
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Skipping {f.name}: no season for date {target_date}"
                                    )
                                )
                                if not options.get("dry_run"):
                                    try:
                                        dest = discarded_dir / f.name
                                        shutil.move(str(f), str(dest))
                                        self.stdout.write(
                                            self.style.SUCCESS(
                                                f"Moved {f.name} -> {dest} (discarded)"
                                            )
                                        )
                                    except Exception:
                                        self.stdout.write(
                                            self.style.WARNING(
                                                f"Failed to move {f.name} to discarded"
                                            )
                                        )
                                continue

                            race = Race.objects.create(
                                season=season,
                                round_number=round_number,
                                circuit=circuit,
                                race_date=target_date,
                                status=session_status,
                            )
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Created Race {race.id} for circuit {circuit} on {target_date} (season {season})"
                                )
                            )
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"Could not read JSON {f.name}: {e}")
                )

            try:
                if race:
                    pr.handle(file=str(f), race_id=race.id)
                elif "season" in info and "round" in info:
                    pr.handle(file=str(f), season=info["season"], round=info["round"])
                else:
                    # try date-based matching using datetime parsed from filename
                    dt = info.get("datetime")
                    if dt:
                        target_date = dt.date()
                        window = timedelta(days=3)
                        candidates = list(
                            Race.objects.filter(
                                race_date__range=(
                                    target_date - window,
                                    target_date + window,
                                )
                            )
                        )
                        if candidates:
                            # prefer candidate with the same session status
                            desired_status = "practice"
                            if info.get("type"):
                                s = info.get("type").lower()
                                if s in ("qualify", "qualifying"):
                                    desired_status = "qualifying"
                                elif s == "race":
                                    desired_status = "race"

                            desired = next(
                                (c for c in candidates if c.status == desired_status),
                                None,
                            )
                            if desired is None:
                                # pick closest by absolute day difference
                                candidates.sort(
                                    key=lambda r: abs((r.race_date - target_date).days)
                                )
                                race = candidates[0]
                            else:
                                race = desired
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f"Inferred race {race.id} by date proximity ({race.race_date}) to {target_date}"
                                )
                            )
                            pr.handle(file=str(f), race_id=race.id)
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Could not infer race for '{f.name}', skipping. Rename to <season>_<round>_TYPE.json or include TrackName with matching Circuit."
                                )
                            )
                            # move to discarded
                            if not options.get("dry_run"):
                                try:
                                    dest = discarded_dir / f.name
                                    shutil.move(str(f), str(dest))
                                    self.stdout.write(
                                        self.style.SUCCESS(
                                            f"Moved {f.name} -> {dest} (discarded)"
                                        )
                                    )
                                except Exception:
                                    self.stdout.write(
                                        self.style.WARNING(
                                            f"Failed to move {f.name} to discarded"
                                        )
                                    )
                            continue
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Could not infer race for '{f.name}', skipping. Rename to <season>_<round>_TYPE.json or include TrackName with matching Circuit."
                            )
                        )
                        # move to discarded
                        if not options.get("dry_run"):
                            try:
                                dest = discarded_dir / f.name
                                shutil.move(str(f), str(dest))
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f"Moved {f.name} -> {dest} (discarded)"
                                    )
                                )
                            except Exception:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f"Failed to move {f.name} to discarded"
                                    )
                                )
                        continue

                if not options.get("dry_run"):
                    dest = output_dir / f.name
                    shutil.move(str(f), str(dest))
                    self.stdout.write(self.style.SUCCESS(f"Moved {f.name} -> {dest}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed processing {f.name}: {e}"))
