from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.teams.models import Team, Sponsor


class Command(BaseCommand):
    help = "Assign available sponsor templates (team=NULL) as main sponsors to teams."

    def add_arguments(self, parser):
        parser.add_argument(
            "--team", type=int, action="append", help="Team id to assign (can repeat)"
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

        templates = list(Sponsor.objects.filter(team__isnull=True, active=True))
        if not templates:
            self.stdout.write(
                "No available sponsor templates (team=NULL, active=True). Aborting."
            )
            return

        self.stdout.write(
            f"Assigning sponsors to {len(teams)} team(s) using {len(templates)} template(s)"
        )

        assigned = []
        with transaction.atomic():
            for i, team in enumerate(teams):
                # unset previous main sponsors for this team
                prev = Sponsor.objects.filter(team=team, is_main=True)
                if prev.exists():
                    if dry:
                        self.stdout.write(
                            f"Would unset previous main sponsor(s) for team {team}"
                        )
                    else:
                        prev.update(is_main=False, team=None)

                template = templates[i % len(templates)]
                if dry:
                    self.stdout.write(
                        f"Would assign sponsor '{template.name}' -> team {team}"
                    )
                else:
                    template.team = team
                    template.is_main = True
                    template.save(update_fields=["team", "is_main"])
                    assigned.append((team, template))

        if dry:
            self.stdout.write("Dry run complete. No DB changes made.")
        else:
            self.stdout.write(f"Assigned sponsors to {len(assigned)} teams.")
