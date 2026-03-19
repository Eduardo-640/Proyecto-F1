from django.core.management.base import BaseCommand
from django.db import transaction

from apps.teams.models import Team
from apps.races.models import RaceResult, CreditTransaction
from apps.drivers.models import Driver
from apps.races.constants import TransactionType


class Command(BaseCommand):
    help = "Merge duplicate per-driver teams (e.g. 'Tuku - Team', 'Tuku - Team 2') into a single canonical team."

    def handle(self, *args, **options):
        # Find candidate team names that follow the '<Driver> - Team' pattern
        candidates = Team.objects.exclude(name__iexact="Unassigned").order_by(
            "created_at"
        )
        processed = 0
        merged_teams = 0
        with transaction.atomic():
            # Group by driver-like prefix: take teams with ' - Team' in name
            driver_teams = candidates.filter(name__icontains=" - Team")
            prefixes = {}
            for t in driver_teams:
                # take prefix before ' - Team'
                parts = t.name.split(" - Team")
                if not parts:
                    continue
                prefix = parts[0].strip()
                prefixes.setdefault(prefix, []).append(t)

            for prefix, teams in prefixes.items():
                if len(teams) <= 1:
                    continue
                # choose canonical: prefer team that currently has a driver assigned
                canonical = None
                for team in teams:
                    if Driver.objects.filter(team=team).exists():
                        canonical = team
                        break
                if canonical is None:
                    # fallback: earliest created (teams are ordered by created_at)
                    canonical = teams[0]

                duplicates = [t for t in teams if t.id != canonical.id]
                if not duplicates:
                    continue

                # Merge duplicates into canonical
                for dup in duplicates:
                    # move RaceResults
                    rr_qs = RaceResult.objects.filter(team=dup)
                    for rr in rr_qs:
                        rr.team = canonical
                        rr.save(update_fields=["team"])

                    # move credits
                    amt = dup.credits or 0
                    if amt:
                        canonical.credits = (canonical.credits or 0) + amt
                        canonical.save()
                        CreditTransaction.objects.create(
                            team=canonical,
                            amount=amt,
                            transaction_type=TransactionType.ADMIN_ADJUSTMENT,
                            description=f"Merged credits from {dup.name}",
                            race=None,
                        )
                    # reassign drivers pointing to dup to canonical
                    drivers = Driver.objects.filter(team=dup)
                    for d in drivers:
                        d.team = canonical
                        d.save(update_fields=["team"])

                    # finally delete duplicate team
                    dup.delete()
                    merged_teams += 1

                processed += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {processed} prefixes, merged {merged_teams} duplicate teams."
            )
        )
