from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Print counts and missing TeamDevelopment/CarSetupSnapshot for a given season"
    )

    def add_arguments(self, parser):
        parser.add_argument("season", type=int, help="Season id to check")

    def handle(self, *args, **options):
        season_id = options.get("season")
        from apps.teams.models import Team
        from apps.developments.models import TeamDevelopment, CarSetupSnapshot

        teams = list(Team.objects.all())
        print(f"teams: {len(teams)}")
        td_count = TeamDevelopment.objects.filter(season_id=season_id).count()
        snap_count = CarSetupSnapshot.objects.filter(season_id=season_id).count()
        print(f"team_developments (season {season_id}): {td_count}")
        print(f"car_setup_snapshots (season {season_id}): {snap_count}")

        missing_dev = [
            t.name
            for t in teams
            if not TeamDevelopment.objects.filter(team=t, season_id=season_id).exists()
        ]
        missing_snap = [
            t.name
            for t in teams
            if not CarSetupSnapshot.objects.filter(team=t, season_id=season_id).exists()
        ]

        print("missing TeamDevelopment:", missing_dev)
        print("missing CarSetupSnapshot:", missing_snap)

        # Print levels for existing devs
        for dev in TeamDevelopment.objects.filter(season_id=season_id).select_related(
            "team"
        ):
            print(
                f"{dev.team.name}: engine={dev.engine} aero={dev.aerodynamics} chassis={dev.chassis} suspension={dev.suspension} electronics={dev.electronics} bonuses_applied={dev.bonuses_applied}"
            )
