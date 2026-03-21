from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.teams.models import Team
from apps.races.models import CreditTransaction
from apps.races.constants import TransactionType


class Command(BaseCommand):
    help = "Reset all teams' credits to a given value (creates admin transactions)."

    def add_arguments(self, parser):
        parser.add_argument(
            "value", type=int, nargs="?", default=500, help="Credits value to set"
        )
        parser.add_argument(
            "--yes", action="store_true", help="Confirm without interactive prompt"
        )

    def handle(self, *args, **options):
        value = options.get("value")
        confirm = options.get("yes")

        if not confirm:
            self.stdout.write(
                self.style.WARNING(f"About to reset all teams' credits to {value}.")
            )
            ans = input("Type YES to continue: ")
            if ans.strip() != "YES":
                raise CommandError("Aborted by user")

        with transaction.atomic():
            teams = Team.objects.all()
            for t in teams:
                old = t.credits or 0
                t.credits = value
                t.save(update_fields=["credits"])
                CreditTransaction.objects.create(
                    team=t,
                    amount=value - old,
                    transaction_type=TransactionType.ADMIN_ADJUSTMENT,
                    description=f"Reset credits to {value} (admin)",
                )

        self.stdout.write(
            self.style.SUCCESS(f"Reset credits for {teams.count()} teams to {value}.")
        )
