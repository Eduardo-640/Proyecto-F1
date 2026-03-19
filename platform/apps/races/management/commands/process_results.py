import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.races.models import RaceResult, Race, CreditTransaction
from apps.drivers.models import Driver, DriverStanding
from apps.teams.models import Team
from apps.races.constants import TransactionType


# Standard F1 points for top-10 (applies to race sessions)
POINTS_TABLE = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
# Reduced points for qualifying (top-3)
QUALIFY_POINTS = [3, 2, 1]

# Credits multiplier (credits per point)
CREDIT_MULTIPLIER = 10


class Command(BaseCommand):
    help = "Process an exported race results JSON and persist RaceResult, DriverStanding and credit transactions."

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to the results.json file")
        parser.add_argument(
            "--race-id", type=int, help="ID of the Race to attach results to"
        )
        parser.add_argument(
            "--season",
            type=int,
            help="Season id (used with --round if race-id omitted)",
        )
        parser.add_argument(
            "--round",
            type=int,
            help="Round number (used with --season if race-id omitted)",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        # Resolve Race
        race = None
        if options.get("race_id"):
            try:
                race = Race.objects.get(pk=options.get("race_id"))
            except Race.DoesNotExist:
                raise CommandError(f"Race id {options.get('race_id')} not found")
        else:
            season = options.get("season")
            round_number = options.get("round")
            if season is None or round_number is None:
                raise CommandError(
                    "Either --race-id or both --season and --round must be provided"
                )
            try:
                race = Race.objects.get(season_id=season, round_number=round_number)
            except Race.DoesNotExist:
                raise CommandError(
                    f"Race for season={season} round={round_number} not found"
                )

        data = json.loads(path.read_text(encoding="utf-8"))

        results = data.get("Result") or data.get("result") or []
        # Determine session type from JSON (if provided). Expected values: RACE, QUALIFY/QUALIFYING, PRACTICE
        session_type = (data.get("Type") or data.get("Session") or "").strip().lower()
        if session_type in ("qualifying",):
            session_type = "qualify"
        if not results:
            raise CommandError("No results array found in the provided JSON")

        # Filter and sort results by TotalTime > 0 ascending; DNFs (TotalTime==0) go after
        def time_key(r):
            t = r.get("TotalTime") or 0
            return t if t > 0 else 10**12

        sorted_results = sorted(results, key=time_key)

        # determine fastest lap if possible (ignore sentinel 999999999)
        best_lap_vals = [
            r.get("BestLap") for r in results if (r.get("BestLap") or 0) < 999999999
        ]
        fastest_lap_val = min(best_lap_vals) if best_lap_vals else None

        created = 0
        updated = 0
        credit_sum = 0

        with transaction.atomic():
            # No global "Unassigned" fallback by default; we'll create a private team
            # for drivers that lack one. (Keep Unassigned only for truly unknown names.)
            unassigned_team = None

            for idx, r in enumerate(sorted_results, start=1):
                guid = r.get("DriverGuid") or r.get("Guid")
                name = (
                    r.get("DriverName") or r.get("Driver", {}).get("Name") or "Unknown"
                )
                total_time = r.get("TotalTime") or 0
                finished = total_time > 0

                # Find or create driver by steam id (guid). Fallback to name match.
                driver = None
                if guid:
                    driver = Driver.objects.filter(steam_id=guid).first()
                if driver is None:
                    driver = Driver.objects.filter(name__iexact=name).first()
                if driver is None:
                    driver = Driver.objects.create(
                        name=name, steam_id=guid if guid else None
                    )

                # If driver has a team (signal may have created it), use it.
                # Otherwise create a team named '<Driver> - Team' (ensure uniqueness).
                team = driver.team
                if not team:
                    name = driver.name or "Unassigned"
                    if not name or name.lower() in ("unknown", ""):
                        # fallback to a shared Unassigned team
                        team, _ = Team.objects.get_or_create(name="Unassigned")
                    else:
                        base_name = f"{name} - Team"
                        candidate = base_name
                        suffix = 1
                        while Team.objects.filter(name__iexact=candidate).exists():
                            suffix += 1
                            candidate = f"{base_name} {suffix}"
                        team = Team.objects.create(name=candidate)

                position = idx if finished else None
                if not finished:
                    # DNFs get a sequential position after existing placed drivers
                    placed_count = RaceResult.objects.filter(
                        race=race, finished_race=True
                    ).count()
                    position = placed_count + 1

                # Decide points table depending on session type:
                # - 'race' -> full POINTS_TABLE
                # - 'qualify' -> QUALIFY_POINTS (top-3)
                # - 'practice' -> no points
                if session_type == "qualify":
                    source_table = QUALIFY_POINTS
                elif session_type == "practice":
                    source_table = []
                else:
                    # default to race behaviour
                    source_table = POINTS_TABLE

                points_awarded = 0
                if position and position <= len(source_table):
                    points_awarded = source_table[position - 1]

                pole_position = False
                fastest_lap = (
                    (r.get("BestLap") == fastest_lap_val)
                    if fastest_lap_val is not None
                    else False
                )

                # Load existing race result if present to compute deltas (idempotency)
                existing_rr = RaceResult.objects.filter(
                    race=race, driver=driver
                ).first()
                old_points = existing_rr.points_awarded if existing_rr else 0
                old_position = existing_rr.position if existing_rr else None
                old_pole = existing_rr.pole_position if existing_rr else False
                old_fastest = existing_rr.fastest_lap if existing_rr else False
                old_finished = existing_rr.finished_race if existing_rr else False

                rr_defaults = {
                    "team": team,
                    "position": position or 0,
                    "pole_position": pole_position,
                    "fastest_lap": fastest_lap,
                    "finished_race": finished,
                    "points_awarded": points_awarded,
                }

                if existing_rr:
                    # update fields
                    for k, v in rr_defaults.items():
                        setattr(existing_rr, k, v)
                    existing_rr.save()
                    created_flag = False
                    rr = existing_rr
                    updated += 1
                else:
                    rr = RaceResult.objects.create(
                        race=race, driver=driver, **rr_defaults
                    )
                    created_flag = True
                    created += 1

                # Update DriverStanding with deltas
                ds, _ = DriverStanding.objects.get_or_create(
                    driver=driver, season=race.season
                )

                # Points delta
                points_delta = points_awarded - old_points
                if points_delta != 0:
                    ds.total_points = max(0, ds.total_points + points_delta)

                # races_entered adjustments
                if created_flag and finished:
                    ds.races_entered += 1
                elif not created_flag:
                    if finished and not old_finished:
                        ds.races_entered += 1
                    elif not finished and old_finished:
                        ds.races_entered = max(0, ds.races_entered - 1)

                # wins
                if old_position == 1 and position != 1:
                    ds.wins = max(0, ds.wins - 1)
                if position == 1 and old_position != 1:
                    ds.wins += 1

                # podiums
                old_podium = old_position is not None and 1 <= old_position <= 3
                new_podium = position is not None and 1 <= position <= 3
                if old_podium and not new_podium:
                    ds.podiums = max(0, ds.podiums - 1)
                if new_podium and not old_podium:
                    ds.podiums += 1

                # pole positions
                if old_pole and not pole_position:
                    ds.pole_positions = max(0, ds.pole_positions - 1)
                if pole_position and not old_pole:
                    ds.pole_positions += 1

                # fastest laps
                if old_fastest and not fastest_lap:
                    ds.fastest_laps = max(0, ds.fastest_laps - 1)
                if fastest_lap and not old_fastest:
                    ds.fastest_laps += 1

                # DNF count
                if old_finished and not finished:
                    ds.dnf_count += 1
                if (
                    not old_finished
                    and finished
                    and existing_rr
                    and existing_rr.finished_race is False
                ):
                    # previously DNF, now finished
                    ds.dnf_count = max(0, ds.dnf_count - 1)

                ds.save()

                # Award credits to the team based on points delta
                credit_delta = points_delta * CREDIT_MULTIPLIER
                if credit_delta != 0:
                    team.credits = (team.credits or 0) + credit_delta
                    team.save()
                    CreditTransaction.objects.create(
                        team=team,
                        amount=credit_delta,
                        transaction_type=TransactionType.RACE_RESULT,
                        description=f"Race rewards delta for position {position}",
                        race=race,
                    )
                    credit_sum += credit_delta

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed file {path.name}: created={created} updated={updated} credits_awarded={credit_sum}"
            )
        )
