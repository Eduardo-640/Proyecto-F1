from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.teams.models import Sponsor


class Command(BaseCommand):
    help = "Delete sponsors. By default deletes only template sponsors (team is null). Use --all to remove all sponsors."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Delete all sponsor records, including assigned ones",
        )
        parser.add_argument("--yes", action="store_true", help="Confirm without prompt")

    def handle(self, *args, **options):
        delete_all = options.get("all")
        confirm = options.get("yes")

        qs = (
            Sponsor.objects.all()
            if delete_all
            else Sponsor.objects.filter(team__isnull=True)
        )
        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.NOTICE("No sponsors to delete."))
            return

        if not confirm:
            self.stdout.write(
                self.style.WARNING(f"About to delete {count} sponsor(s).")
            )
            ans = input("Type YES to continue: ")
            if ans.strip() != "YES":
                raise CommandError("Aborted by user")

        with transaction.atomic():
            qs.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted {count} sponsor(s)."))
