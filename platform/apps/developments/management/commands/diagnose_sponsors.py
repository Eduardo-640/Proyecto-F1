from django.core.management.base import BaseCommand
import json


class Command(BaseCommand):
    help = "Diagnose sponsor bonuses and team development states"

    def add_arguments(self, parser):
        parser.add_argument(
            "--season", dest="season", default=None, help="Season name or id to inspect"
        )

    def handle(self, *args, **options):
        from apps.seasons.models import Season
        from apps.teams.models import Team
        from apps.developments.setup_service import (
            get_starting_department_bonus,
            get_sponsor_money_multiplier,
        )
        from apps.developments.models import TeamDevelopment

        season_q = options.get("season")
        season = None
        if season_q:
            try:
                season = Season.objects.get(pk=int(season_q))
            except Exception:
                try:
                    season = Season.objects.get(name__icontains=season_q)
                except Exception:
                    season = None

        teams = Team.objects.all()
        for t in teams:
            sponsor = getattr(t, "main_sponsor", None)
            bonuses = {}
            mult = None
            if sponsor:
                bonuses = get_starting_department_bonus(t)
                mult = get_sponsor_money_multiplier(t)

            levels = {}
            if season:
                try:
                    dev = TeamDevelopment.objects.get(team=t, season=season)
                    for d in [
                        "engine",
                        "aerodynamics",
                        "chassis",
                        "suspension",
                        "electronics",
                    ]:
                        levels[d] = dev.get_level(d)
                except TeamDevelopment.DoesNotExist:
                    levels = {}

            conds = []
            if sponsor:
                for c in sponsor.conditions.all():
                    conds.append(
                        {"category": c.category, "type": c.type, "value": str(c.value)}
                    )

            out = {
                "team": t.name,
                "sponsor": sponsor.name if sponsor else None,
                "conditions": conds,
                "bonuses_calc": bonuses,
                "money_multiplier": mult,
                "levels": levels,
            }
            self.stdout.write(json.dumps(out, ensure_ascii=False))
