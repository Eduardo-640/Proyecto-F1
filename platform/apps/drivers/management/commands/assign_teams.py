from django.core.management.base import BaseCommand
from django.db import transaction

from apps.drivers.models import Driver
from apps.teams.models import Team


class Command(BaseCommand):
    help = "Create individual teams for drivers that have no team or are assigned to 'Unassigned'"

    def handle(self, *args, **options):
        with transaction.atomic():
            drivers = Driver.objects.filter(
                team__name__iexact="Unassigned"
            ) | Driver.objects.filter(team__isnull=True)
            drivers = drivers.distinct()
            created = 0
            for d in drivers:
                name = d.name or "Unnamed"
                base = f"{name} - Team"
                candidate = base
                suffix = 1
                while Team.objects.filter(name__iexact=candidate).exists():
                    suffix += 1
                    candidate = f"{base} {suffix}"
                team = Team.objects.create(name=candidate)
                d.team = team
                d.save(update_fields=["team"])
                created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Assigned team '{team.name}' to driver {d.name} (id={d.id})"
                    )
                )

            if created == 0:
                self.stdout.write("No drivers needed reassignment.")
            else:
                self.stdout.write(
                    self.style.SUCCESS(f"Created and assigned {created} teams.")
                )
