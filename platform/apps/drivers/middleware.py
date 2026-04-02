from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from apps.drivers.models import Driver


class DriverUser:
    def __init__(self, driver, driver_id, steam_id, driver_name):
        self.driver = driver
        self.driver_id = driver_id
        self.driver_steam_id = steam_id
        self.driver_name = driver_name
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return f"Driver: {self.driver_name}"


class DriverJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            driver_id = validated_token["driver_id"]
        except KeyError:
            raise InvalidToken("Token contained no recognizable driver identification")

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            raise InvalidToken("No driver found for this token")

        return DriverUser(
            driver=driver,
            driver_id=driver_id,
            steam_id=validated_token.get("steam_id"),
            driver_name=validated_token.get("driver_name"),
        )
