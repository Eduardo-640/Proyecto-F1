import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.teams.models import Sponsor, SponsorCondition
from apps.developments.constants import Department


DEPARTMENTS = [d.value for d in Department]


class Command(BaseCommand):
    help = "Load sponsors from a JSON file. Validates departments and ensures at least one positive and one negative condition per sponsor (auto-fills if needed)."

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to sponsors JSON file")
        parser.add_argument(
            "--update", action="store_true", help="Update existing sponsors by name"
        )
        parser.add_argument(
            "--affinity-total",
            dest="affinity_total",
            type=int,
            default=1,
            help="Número total de puntos positivos (affinity) por sponsor (excluyendo money). Set to 0 to disable enforcement.",
        )

    def handle(self, *args, **options):
        path = Path(options.get("file"))
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise CommandError("JSON must be an array of sponsor objects")

        created = 0
        updated = 0
        skipped = 0

        with transaction.atomic():
            for entry in data:
                name = entry.get("name")
                if not name:
                    skipped += 1
                    continue

                sponsor_values = {
                    "name": name,
                    "description": entry.get("description", ""),
                    "is_main": entry.get("is_main", False),
                    "base_bonus": int(entry.get("base_bonus", 0)),
                    "active": bool(entry.get("active", True)),
                }

                sponsor, created_flag = Sponsor.objects.get_or_create(
                    name=name, defaults=sponsor_values
                )
                if not created_flag and options.get("update"):
                    for k, v in sponsor_values.items():
                        setattr(sponsor, k, v)
                    sponsor.save()

                if created_flag:
                    created += 1
                else:
                    updated += 1

                # load conditions from entry
                conds = entry.get("conditions", [])
                # build mapping category -> value
                cat_map = {
                    c.get("category"): int(c.get("value", 0))
                    for c in conds
                    if c.get("category")
                }

                # ensure every department exists in conditions; if missing, set 0
                for dept in DEPARTMENTS:
                    if dept not in cat_map:
                        cat_map[dept] = 0

                # normalization rules:
                # - for 'money' keep integer and force at least 1
                # - for other categories normalize to -1/0/+1
                for dept in DEPARTMENTS:
                    v = int(cat_map.get(dept, 0))
                    if dept == "money":
                        cat_map[dept] = max(1, v) if v != 0 else 1
                    else:
                        cat_map[dept] = 0 if v == 0 else (1 if v > 0 else -1)

                # enforce affinity_total (number of positive affinities excluding money)
                affinity_total = int(options.get("affinity_total", 1))
                cats_no_money = [c for c in DEPARTMENTS if c != "money"]
                if affinity_total and affinity_total > 0:
                    positives = [c for c in cats_no_money if cat_map.get(c, 0) > 0]
                    # add positives if too few
                    if len(positives) < affinity_total:
                        choices = [c for c in cats_no_money if cat_map.get(c, 0) == 0]
                        while len(positives) < affinity_total and choices:
                            pick = random.choice(choices)
                            cat_map[pick] = 1
                            positives.append(pick)
                            choices.remove(pick)
                    # reduce positives if too many
                    if len(positives) > affinity_total:
                        to_remove = len(positives) - affinity_total
                        for _ in range(to_remove):
                            rem = random.choice(positives)
                            cat_map[rem] = 0
                            positives.remove(rem)

                # ensure at least one negative among non-money
                negatives = [c for c in cats_no_money if cat_map.get(c, 0) < 0]
                if not negatives:
                    zeros = [c for c in cats_no_money if cat_map.get(c, 0) == 0]
                    if zeros:
                        cat_map[random.choice(zeros)] = -1
                    else:
                        # fallback: flip one positive if exists
                        positives = [c for c in cats_no_money if cat_map.get(c, 0) > 0]
                        if positives:
                            flip = random.choice(positives)
                            cat_map[flip] = -1

                # delete previous conditions for this sponsor and recreate
                SponsorCondition.objects.filter(sponsor=sponsor).delete()
                # compute total score (exclude money)
                total_score = sum(int(v) for k, v in cat_map.items() if k != "money")
                sponsor.total_score = int(total_score)
                sponsor.save()

                for cat in DEPARTMENTS:
                    val = int(cat_map.get(cat, 0))
                    # determine type: money special, zero -> neutral
                    if cat == "money":
                        typ = "money" if val != 0 else "neutral"
                    else:
                        if val == 0:
                            typ = "neutral"
                        else:
                            typ = "affinity" if val > 0 else "penalty"

                    SponsorCondition.objects.create(
                        sponsor=sponsor,
                        type=typ,
                        category=cat,
                        value=val,
                        description=f"Auto-generated from import (category={cat})",
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sponsors created={created} updated={updated} skipped={skipped}"
            )
        )
