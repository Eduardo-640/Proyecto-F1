"""
balance_sponsors
================
Ensures every Sponsor has a SponsorCondition row for each of the
canonical non-money categories, fills missing ones as neutral/0,
then (optionally) rebalances so that each sponsor has the same
number of affinities (+1) as penalties (-1), i.e. total_score == 0.

Usage
-----
    # Check only — report unbalanced sponsors without touching the DB
    python manage.py balance_sponsors

    # Fill missing categories and rebalance all sponsors
    python manage.py balance_sponsors --fix

    # Only fill missing categories (skip rebalancing)
    python manage.py balance_sponsors --fill-only
"""

import random
from django.core.management.base import BaseCommand
from apps.teams.models import Sponsor, SponsorCondition

# Canonical set of non-money categories (must match the CSV / admin import)
NON_MONEY_CATS = [
    "engine",
    "aerodynamics",
    "electronics",
    "chassis",
    "suspension",
    "development",
    "consistency",
    "podiums",
    "wins",
    "points",
    "speed",
]
ALL_CATS = NON_MONEY_CATS + ["money"]


class Command(BaseCommand):
    help = "Fill missing SponsorCondition rows and optionally rebalance affinities/penalties."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            default=False,
            help="Fill missing categories AND rebalance each sponsor to total_score == 0.",
        )
        parser.add_argument(
            "--fill-only",
            action="store_true",
            default=False,
            help="Fill missing categories with neutral/0 but do NOT rebalance.",
        )

    def handle(self, *args, **options):
        fix = options["fix"]
        fill_only = options["fill_only"]

        filled_total = 0
        rebalanced_total = 0
        unbalanced = []

        for sponsor in Sponsor.objects.prefetch_related("conditions").all():
            # Index existing conditions by category
            existing = {c.category: c for c in sponsor.conditions.all()}

            # ── 1. Fill missing categories ──────────────────────────────────
            if fix or fill_only:
                for cat in ALL_CATS:
                    if cat not in existing:
                        val = 1 if cat == "money" else 0
                        typ = None if cat == "money" else "neutral"
                        cond = SponsorCondition.objects.create(
                            sponsor=sponsor,
                            type=typ,
                            category=cat,
                            value=val,
                            description=f"Auto-filled: {cat} {val}",
                        )
                        existing[cat] = cond
                        filled_total += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"  [{sponsor.name}] filled missing '{cat}' as neutral/0"
                            )
                        )

            # ── 2. Compute balance ──────────────────────────────────────────
            non_money_conds = [existing[c] for c in NON_MONEY_CATS if c in existing]
            affinities = [c for c in non_money_conds if int(c.value) > 0]
            penalties = [c for c in non_money_conds if int(c.value) < 0]
            total_score = sum(int(c.value) for c in non_money_conds)

            if total_score != 0:
                unbalanced.append(
                    (
                        sponsor.id,
                        sponsor.name,
                        total_score,
                        len(affinities),
                        len(penalties),
                    )
                )

            # ── 3. Rebalance ────────────────────────────────────────────────
            if fix and total_score != 0:
                # Iteratively neutralise the excess side until balanced
                iterations = 0
                while total_score != 0 and iterations < 20:
                    iterations += 1
                    if total_score < 0:
                        # excess penalties — neutralise one
                        targets = [c for c in non_money_conds if int(c.value) < 0]
                        if not targets:
                            break
                        victim = random.choice(targets)
                        victim.value = 0
                        victim.type = "neutral"
                        victim.description = (
                            f"Rebalanced: neutralised penalty on {victim.category}"
                        )
                        victim.save(update_fields=["value", "type", "description"])
                        total_score += 1
                    else:
                        # excess affinities — neutralise one
                        targets = [c for c in non_money_conds if int(c.value) > 0]
                        if not targets:
                            break
                        victim = random.choice(targets)
                        victim.value = 0
                        victim.type = "neutral"
                        victim.description = (
                            f"Rebalanced: neutralised affinity on {victim.category}"
                        )
                        victim.save(update_fields=["value", "type", "description"])
                        total_score -= 1

                    # refresh non_money_conds after update
                    non_money_conds = [
                        existing[c] for c in NON_MONEY_CATS if c in existing
                    ]

                rebalanced_total += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [{sponsor.name}] rebalanced → total_score={total_score}"
                    )
                )

            # ── 4. Save total_score ─────────────────────────────────────────
            new_total = sum(
                int(c.value) for c in sponsor.conditions.exclude(category="money")
            )
            if sponsor.total_score != new_total:
                sponsor.total_score = new_total
                sponsor.save(update_fields=["total_score"])

        # ── Summary ──────────────────────────────────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Conditions filled:    {filled_total}"))
        self.stdout.write(
            self.style.SUCCESS(f"Sponsors rebalanced:  {rebalanced_total}")
        )

        if unbalanced and not fix:
            self.stdout.write(
                self.style.WARNING(
                    f"\nUnbalanced sponsors ({len(unbalanced)}) — run with --fix to auto-rebalance:"
                )
            )
            self.stdout.write(
                f"  {'ID':>4}  {'Name':<40}  {'score':>6}  {'aff':>4}  {'pen':>4}"
            )
            for sid, sname, score, aff, pen in unbalanced:
                self.stdout.write(
                    f"  {sid:>4}  {sname:<40}  {score:>6}  {aff:>4}  {pen:>4}"
                )
        elif not unbalanced:
            self.stdout.write(
                self.style.SUCCESS("All sponsors are balanced (total_score == 0).")
            )
