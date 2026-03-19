from django.core.management.base import BaseCommand

from apps.teams.models import SponsorCondition
from apps.teams.constants import Affinity
from apps.developments.constants import Department


ALIASES = {
    "aero": "aerodynamics",
}


def valid_category_set() -> set[str]:
    return set([c.value for c in Affinity]) | set([c.value for c in Department])


class Command(BaseCommand):
    help = (
        "Validate SponsorCondition.category values and optionally fix common aliases."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Attempt to fix common aliases (e.g., 'aero' -> 'aerodynamics')",
        )

    def handle(self, *args, **options):
        fix = options.get("fix")
        valid = valid_category_set()
        total = 0
        invalid = []

        for sc in SponsorCondition.objects.all():
            total += 1
            cat = sc.category
            if cat not in valid:
                invalid.append((sc.pk, sc.sponsor_id, cat))

        if not invalid:
            self.stdout.write(
                f"All {total} SponsorCondition entries have valid categories."
            )
            return

        self.stdout.write(f"Found {len(invalid)} invalid SponsorCondition categories:")
        for pk, sponsor_id, cat in invalid:
            self.stdout.write(f" - id={pk} sponsor={sponsor_id} category='{cat}'")

        if fix:
            changed = 0
            for pk, sponsor_id, cat in invalid:
                if cat in ALIASES:
                    new = ALIASES[cat]
                    sc = SponsorCondition.objects.get(pk=pk)
                    sc.category = new
                    sc.save(update_fields=["category"])
                    self.stdout.write(f"Fixed id={pk}: '{cat}' -> '{new}'")
                    changed += 1
            self.stdout.write(f"Fixed {changed} entries (of {len(invalid)} invalid).")
        else:
            self.stdout.write(
                "Run with --fix to attempt automatic fixes for known aliases."
            )
