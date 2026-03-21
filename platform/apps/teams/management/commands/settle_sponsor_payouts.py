from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.races.models import Race, RaceResult
from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType
from apps.teams.models import Sponsor, SponsorPayout
from apps.developments.constants import PAYOUT_CONDITION_BOOST

# Fraction of base_bonus applied upfront (must match apply_sponsor_base)
UPFRONT_PERCENT = 0.25
UPFRONT_CAP = 2000

# Fraction of remaining payout applied per race (before performance modifier)
PAYOUT_RATE_PER_RACE = 0.25


def _build_race_team_stats(race):
    """Return a dict {team_id: {points, best_position, has_win, has_podium, has_points, fastest_lap}}
    aggregated from all RaceResult rows for this race.

    fastest_lap is True/False/None:
      True  – this team's driver recorded the fastest lap
      False – another driver recorded it
      None  – no driver in the race has fastest_lap=True (data unknown, e.g. manual entry)
              In this case speed conditions must be skipped to avoid unfair penalties.
    """
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
    any_fastest_lap = False
    for rr in RaceResult.objects.filter(race=race).select_related("team"):
        tid = rr.team.id
        stats[tid]["points"] += rr.points_awarded or 0
        if rr.position and rr.position < stats[tid]["best_position"]:
            stats[tid]["best_position"] = rr.position
        if rr.fastest_lap:
            stats[tid]["fastest_lap"] = True
            any_fastest_lap = True
    for tid, s in stats.items():
        s["has_win"] = s["best_position"] == 1
        s["has_podium"] = s["best_position"] <= 3
        s["has_points"] = s["points"] > 0
        # If no driver in the race has fastest_lap flagged, mark as None (unknown)
        # so that speed conditions are skipped rather than penalised unfairly.
        if not any_fastest_lap:
            s["fastest_lap"] = None
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

        # If fastest_lap data is unknown (None), skip speed conditions entirely
        # to avoid penalising teams for data that was never recorded.
        if cond_key == "fastest_lap" and team_stat.get("fastest_lap") is None:
            continue

        achieved = (
            (cond_key == "win" and team_stat.get("has_win"))
            or (cond_key == "podium" and team_stat.get("has_podium"))
            or (cond_key == "any_points" and team_stat.get("has_points"))
            or (cond_key == "fastest_lap" and team_stat.get("fastest_lap") is True)
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
            # Lazy-init: create SponsorPayout for any active sponsor assigned to a race
            # team that does not yet have a payout record for this season.
            # This handles teams that joined after apply_sponsor_base ran, or where
            # the command was never called for that sponsor.
            race_team_ids = set(team_points.keys())
            for sponsor in Sponsor.objects.filter(
                active=True, team_id__in=race_team_ids, base_bonus__gt=0
            ).select_related("team"):
                already_exists = SponsorPayout.objects.filter(
                    sponsor=sponsor, team=sponsor.team, season=race.season
                ).exists()
                if not already_exists:
                    upfront = min(
                        int(round(sponsor.base_bonus * UPFRONT_PERCENT)), UPFRONT_CAP
                    )
                    remainder = sponsor.base_bonus - upfront
                    # Give the upfront credit that apply_sponsor_base would have given
                    if upfront > 0:
                        sponsor.team.credits = (sponsor.team.credits or 0) + upfront
                        sponsor.team.save(update_fields=["credits"])
                        CreditTransaction.objects.create(
                            team=sponsor.team,
                            amount=upfront,
                            transaction_type=TransactionType.SPONSOR_BASE,
                            description=f"Sponsor upfront (auto-init) {sponsor.name} season:{race.season_id}",
                        )
                    if remainder > 0:
                        SponsorPayout.objects.create(
                            sponsor=sponsor,
                            team=sponsor.team,
                            season=race.season,
                            total_amount=sponsor.base_bonus,
                            remaining_amount=remainder,
                        )

            # find payouts for teams that have entries in this race and remaining > 0 in same season
            payouts = SponsorPayout.objects.filter(
                remaining_amount__gt=0,
                team__in=race_team_ids,
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
