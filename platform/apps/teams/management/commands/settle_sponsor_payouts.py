from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.races.models import Race, RaceResult
from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType
from apps.teams.models import SponsorPayout
from apps.developments.constants import PAYOUT_CONDITION_BOOST

# Fraction of remaining payout applied per race (before performance modifier)
PAYOUT_RATE_PER_RACE = 0.25


def _build_race_team_stats(race):
    """Return a dict {team_id: {points, position, has_podium, has_win, has_fastest_lap, has_points}}
    aggregated from all RaceResult rows for this race."""
    from collections import defaultdict

    stats = defaultdict(
        lambda: {
            "points": 0,
            "best_position": 99,
            "fastest_lap": False,
            "has_win": False,
            "has_podium": False,
            "has_points": False,
        }
    )
    for rr in RaceResult.objects.filter(race=race).select_related("team"):
        tid = rr.team.id
        stats[tid]["points"] += rr.points_awarded or 0
        if rr.position and rr.position < stats[tid]["best_position"]:
            stats[tid]["best_position"] = rr.position
        if rr.fastest_lap:
            stats[tid]["fastest_lap"] = True
    for tid, s in stats.items():
        s["has_win"] = s["best_position"] == 1
        s["has_podium"] = s["best_position"] <= 3
        s["has_points"] = s["points"] > 0
    return stats


def _sponsor_perf_multiplier(sponsor, team_stat) -> float:
    """Return a payout multiplier modifier from sponsor conditions for this race.

    Each performance condition (wins, podiums, consistency, speed, points) checks
    whether the team achieved the required result and applies ±bonus*value.
    Result is clamped to [0.5, 2.0] relative to base 1.0.
    """
    modifier = 0.0
    for cond in sponsor.conditions.filter(category__in=PAYOUT_CONDITION_BOOST.keys()):
        rule = PAYOUT_CONDITION_BOOST.get(cond.category)
        if not rule:
            continue
        try:
            val = int(cond.value)
        except Exception:
            continue
        if val == 0:
            continue

        cond_key = rule["condition"]
        achieved = (
            (cond_key == "win" and team_stat.get("has_win"))
            or (cond_key == "podium" and team_stat.get("has_podium"))
            or (cond_key == "any_points" and team_stat.get("has_points"))
            or (cond_key == "fastest_lap" and team_stat.get("fastest_lap"))
        )
        # affinity (+1) rewards achievement; penalty (-1) rewards NOT achieving
        if val > 0 and achieved:
            modifier += rule["bonus"]
        elif val < 0 and not achieved:
            modifier += rule["bonus"]  # penalty sponsor rewards the failure scenario
        elif val > 0 and not achieved:
            modifier -= rule["bonus"] * 0.5  # underperformance deduction (half)
        # val < 0 and achieved → no modifier (team did well despite penalty sponsor)

    return max(0.5, min(2.0, 1.0 + modifier))


class Command(BaseCommand):
    help = "Settle sponsor pending payouts for a race based on results (performance)."

    def add_arguments(self, parser):
        parser.add_argument("race_id", type=int, help="Race id to settle payouts for")

    def handle(self, *args, **options):
        race_id = options.get("race_id")
        try:
            race = Race.objects.get(pk=int(race_id))
        except Race.DoesNotExist:
            raise CommandError(f"Race id {race_id} not found")

        results_qs = RaceResult.objects.filter(race=race)
        if not results_qs.exists():
            self.stdout.write(
                self.style.NOTICE(f"No results for race {race}; nothing to settle.")
            )
            return

        # compute team points in this race
        team_points = {}
        for rr in results_qs:
            team = rr.team
            team_points[team.id] = team_points.get(team.id, 0) + (
                rr.points_awarded or 0
            )

        if not team_points:
            self.stdout.write(
                self.style.NOTICE("No points awarded in this race — no payouts.")
            )
            return

        max_points = max(team_points.values())
        if max_points <= 0:
            self.stdout.write(
                self.style.NOTICE("Max points is zero — no performance-based payouts.")
            )
            return

        applied = 0
        skipped = 0
        with transaction.atomic():
            # find payouts for teams that have entries in this race and remaining > 0 in same season
            payouts = SponsorPayout.objects.filter(
                remaining_amount__gt=0,
                team__in=[t for t in team_points.keys()],
                season=race.season,
            ).select_related("sponsor", "team")

            # build per-team race stats once
            team_stats = _build_race_team_stats(race)

            for p in payouts:
                team_id = p.team.id
                points = team_points.get(team_id, 0)
                if points <= 0:
                    skipped += 1
                    continue

                perf = float(points) / float(max_points)

                # Apply sponsor-condition performance modifier
                stat = team_stats.get(team_id, {})
                sponsor_mult = _sponsor_perf_multiplier(p.sponsor, stat)
                pay = int(
                    round(
                        p.remaining_amount * PAYOUT_RATE_PER_RACE * perf * sponsor_mult
                    )
                )
                if pay <= 0:
                    skipped += 1
                    continue

                marker = f"sponsor_payout:race:{race.id}:payout:{p.id}"
                exists = CreditTransaction.objects.filter(
                    team=p.team,
                    transaction_type=TransactionType.SPONSOR_PAYOUT,
                    description__contains=marker,
                ).exists()
                if exists:
                    skipped += 1
                    continue

                # apply payment
                p.remaining_amount = max(0, p.remaining_amount - pay)
                p.save(update_fields=["remaining_amount"])  # persist remainder

                CreditTransaction.objects.create(
                    team=p.team,
                    amount=pay,
                    transaction_type=TransactionType.SPONSOR_PAYOUT,
                    description=f"Sponsor payout {p.sponsor.name} ({marker})",
                    race=race,
                )
                applied += 1

        self.stdout.write(self.style.SUCCESS(f"Applied: {applied}; skipped: {skipped}"))
