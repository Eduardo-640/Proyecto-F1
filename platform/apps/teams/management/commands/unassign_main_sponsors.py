from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.teams.models import Team, Sponsor


class Command(BaseCommand):
    help = "Unassign main sponsors from selected teams (sets sponsor.team=None and is_main=False)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--team", type=int, action="append", help="Team id to unassign (can repeat)"
        )
        parser.add_argument(
            "--all", action="store_true", help="Apply to all active teams"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without changing DB",
        )

    def handle(self, *args, **options):
        team_ids = options.get("team") or []
        apply_all = options.get("all")
        dry = options.get("dry_run")

        if not apply_all and not team_ids:
            raise CommandError("Provide --team TEAM_ID or --all to target teams")

        if apply_all:
            teams = list(Team.objects.filter(active=True))
        else:
            teams = list(Team.objects.filter(id__in=team_ids))

        if not teams:
            self.stdout.write("No teams found for the given criteria.")
            return

        total_unassigned = 0
        with transaction.atomic():
            for team in teams:
                q = Sponsor.objects.filter(team=team, is_main=True)
                cnt = q.count()
                if cnt == 0:
                    self.stdout.write(f"No main sponsor for team {team}")
                    continue
                if dry:
                    self.stdout.write(
                        f"Would unassign {cnt} sponsor(s) from team {team}"
                    )
                else:
                    q.update(is_main=False, team=None)
                    total_unassigned += cnt

        if dry:
            self.stdout.write("Dry run complete. No DB changes made.")
        else:
            self.stdout.write(f"Unassigned {total_unassigned} sponsor record(s).")
