from django.core.management.base import BaseCommand
from apps.drivers.models import Driver


class Command(BaseCommand):
    help = 'Set password for an existing driver'

    def add_arguments(self, parser):
        parser.add_argument('steam_id', type=str, help='Steam ID of the driver')
        parser.add_argument('password', type=str, help='New password')

    def handle(self, *args, **options):
        steam_id = options['steam_id']
        password = options['password']

        try:
            driver = Driver.objects.get(steam_id=steam_id)
            driver.set_password(password)
            driver.save()
            self.stdout.write(
                self.style.SUCCESS(f'Password set successfully for driver: {driver.name} ({steam_id})')
            )
        except Driver.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Driver with steam_id {steam_id} not found')
            )
