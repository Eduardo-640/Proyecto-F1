from django.core.management.base import BaseCommand
from django.db import transaction

from apps.teams.models import Team
from apps.races.models import RaceResult
from apps.drivers.models import Driver
from apps.races.management.commands.process_results import CREDIT_MULTIPLIER
from apps.races.constants import TransactionType
from apps.races.models import CreditTransaction


class Command(BaseCommand):
    help = "Redistribute credits and reassign RaceResults from 'Unassigned' team to each driver's personal team."

    def handle(self, *args, **options):
        unassigned = Team.objects.filter(name__iexact="Unassigned").first()
        if not unassigned:
            self.stdout.write(self.style.WARNING("No 'Unassigned' team found."))
            return

        results = RaceResult.objects.filter(team=unassigned).select_related(
            "driver", "race"
        )
        if not results.exists():
            self.stdout.write(
                self.style.SUCCESS("No RaceResults assigned to 'Unassigned'.")
            )
            return

        moved = 0
        credit_moved = 0
        with transaction.atomic():
            for rr in results:
                driver = rr.driver
                # ensure driver has a team (signal should have created one)
                team = driver.team
                if not team:
                    # create a team for driver
                    base = f"{driver.name} - Team" if driver.name else "Unnamed - Team"
                    candidate = base
                    suffix = 1
                    while Team.objects.filter(name__iexact=candidate).exists():
                        suffix += 1
                        candidate = f"{base} {suffix}"
                    team = Team.objects.create(name=candidate)
                    driver.team = team
                    driver.save(update_fields=["team"])

                # compute credit amount awarded for this result
                pts = rr.points_awarded or 0
                credit = pts * CREDIT_MULTIPLIER

                # transfer credits
                if credit:
                    unassigned.credits = max(0, (unassigned.credits or 0) - credit)
                    unassigned.save()

                    team.credits = (team.credits or 0) + credit
                    team.save()

                    # create mirror transactions for audit
                    CreditTransaction.objects.create(
                        team=unassigned,
                        amount=-credit,
                        transaction_type=TransactionType.ADMIN_ADJUSTMENT,
                        description=f"Redistribution to {team.name} for driver {driver.name} (race {rr.race_id})",
                        race=rr.race,
                    )
                    CreditTransaction.objects.create(
                        team=team,
                        amount=credit,
                        transaction_type=TransactionType.ADMIN_ADJUSTMENT,
                        description=f"Redistribution from Unassigned for driver {driver.name} (race {rr.race_id})",
                        race=rr.race,
                    )
                    credit_moved += credit

                # reassign RaceResult.team
                rr.team = team
                rr.save(update_fields=["team"])
                moved += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Reassigned {moved} RaceResults and moved {credit_moved} credits."
            )
        )
