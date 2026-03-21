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

                # ensure at least one positive and one negative exists
                has_pos = any(v > 0 for v in cat_map.values())
                has_neg = any(v < 0 for v in cat_map.values())
                # auto-fill if missing: add small +1 to first dept and -1 to second
                if not has_pos:
                    first = DEPARTMENTS[0]
                    cat_map[first] = 1
                if not has_neg:
                    second = DEPARTMENTS[1] if len(DEPARTMENTS) > 1 else DEPARTMENTS[0]
                    # avoid clobbering if already +1; set to -1
                    if cat_map.get(second, 0) > 0:
                        # find any dept with zero
                        zero_dept = next(
                            (d for d in DEPARTMENTS if cat_map.get(d, 0) == 0), None
                        )
                        if zero_dept:
                            cat_map[zero_dept] = -1
                        else:
                            cat_map[second] = -1
                    else:
                        cat_map[second] = -1

                # delete previous conditions for this sponsor and recreate
                SponsorCondition.objects.filter(sponsor=sponsor).delete()
                for cat, val in cat_map.items():
                    SponsorCondition.objects.create(
                        sponsor=sponsor,
                        type="affinity" if val >= 0 else "penalty",
                        category=cat,
                        value=val,
                        description=f"Auto-generated from import (category={cat})",
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Sponsors created={created} updated={updated} skipped={skipped}"
            )
        )
