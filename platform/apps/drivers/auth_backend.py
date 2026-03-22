from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import AnonymousUser
from .models import Driver


class DriverBackend(BaseBackend):
    """
    Backend de autenticación que usa el modelo Driver en lugar de User.
    Autentica usando steam_id y password.
    """

    def authenticate(self, request, steam_id=None, password=None, **kwargs):
        if steam_id is None or password is None:
            return None

        try:
            driver = Driver.objects.get(steam_id=steam_id, active=True)
            if driver and driver.check_password(password):
                return driver
        except Driver.DoesNotExist:
            return None

        return None

    def get_user(self, driver_id):
        try:
            return Driver.objects.get(pk=driver_id, active=True)
        except Driver.DoesNotExist:
            return None