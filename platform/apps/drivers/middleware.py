from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.utils.deprecation import MiddlewareMixin
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
            driver_id = validated_token['driver_id']
        except KeyError:
            raise InvalidToken('Token contained no recognizable driver identification')

        try:
            driver = Driver.objects.get(id=driver_id)
        except Driver.DoesNotExist:
            raise InvalidToken('No driver found for this token')

        return DriverUser(
            driver=driver,
            driver_id=driver_id,
            steam_id=validated_token.get('steam_id'),
            driver_name=validated_token.get('driver_name'),
        )


class DriverJWTMiddleware(MiddlewareMixin):
    """
    Middleware que extrae información del driver del token JWT
    y la agrega al request para uso en vistas.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Intentar autenticar con JWT personalizado
        auth = DriverJWTAuthentication()
        try:
            # Obtener el token de la request
            auth_result = auth.authenticate(request)

            if auth_result is not None:
                user, token = auth_result

                # Agregar información al request
                request.driver_id = user.driver_id
                request.driver_steam_id = user.driver_steam_id
                request.driver_name = user.driver_name
                request.driver = user.driver
                request.user = user

        except (InvalidToken, TokenError):
            # Token inválido, continuar sin información del driver
            pass

        return None