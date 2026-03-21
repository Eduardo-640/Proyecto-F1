from django.db import transaction
from apps.teams.models import Sponsor, SponsorCondition

CATS = [
    "engine",
    "aerodynamics",
    "electronics",
    "chassis",
    "suspension",
    "development",
    "consistency",
    "podiums",
    "money",
    "speed",
]

with transaction.atomic():
    for s in Sponsor.objects.select_related().all():
        conds = {c.category: c for c in s.conditions.all()}
        changed = False
        for cat in CATS:
            if cat not in conds:
                val = 1 if cat == "money" else 0
                typ = "money" if cat == "money" else "neutral"
                SponsorCondition.objects.create(
                    sponsor=s,
                    type=typ,
                    category=cat,
                    value=val,
                    description="Auto-created (fix script)",
                )
                changed = True
        # recalc total_score excluding money
        conds2 = {c.category: c for c in s.conditions.all()}
        total = sum(int(v.value) for k, v in conds2.items() if k != "money")
        if s.total_score != total:
            s.total_score = int(total)
            s.save()
            changed = True
        if changed:
            print("Updated", s.name, "total_score=", s.total_score)

print("done")
