from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Driver
from .middleware import DriverJWTAuthentication


class DriverLoginView(APIView):
    """Vista de login para drivers usando steam_id y password"""

    permission_classes = [AllowAny]

    def post(self, request):
        steam_id = request.data.get("steam_id")
        password = request.data.get("password")

        if not steam_id or not password:
            return Response(
                {"error": "steam_id y password son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        driver = authenticate(request, steam_id=steam_id, password=password)

        if driver is None:
            return Response(
                {"error": "Credenciales inválidas"}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken()
        refresh["driver_id"] = driver.id
        refresh["steam_id"] = driver.steam_id
        refresh["driver_name"] = driver.name

        access = refresh.access_token
        access["driver_id"] = driver.id
        access["steam_id"] = driver.steam_id
        access["driver_name"] = driver.name

        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
                "driver": {
                    "id": driver.id,
                    "steam_id": driver.steam_id,
                    "name": driver.name,
                    "last_name": driver.last_name,
                    "team": driver.team.name if driver.team else None,
                },
            }
        )


class DriverRegisterView(APIView):
    """Vista de registro para nuevos drivers"""

    permission_classes = [AllowAny]

    def post(self, request):
        steam_id = request.data.get("steam_id")
        password = request.data.get("password")
        name = request.data.get("name")

        if not steam_id or not password or not name:
            return Response(
                {"error": "steam_id, password y name son requeridos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        password_confirmation = request.data.get("password_confirmation")
        if password_confirmation and password != password_confirmation:
            return Response(
                {"error": "Las contraseñas no coinciden"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = Driver.objects.filter(steam_id=steam_id).first()
        if existing is not None:
            if existing.has_usable_password():
                return Response(
                    {"error": "Este Steam ID ya tiene una cuenta. Inicia sesión."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Driver exists but was created by admin without a password → claim it
            existing.set_password(password)
            if name:
                existing.name = name
            last_name = request.data.get("last_name", "")
            if last_name:
                existing.last_name = last_name
            existing.active = True
            existing.save(update_fields=["password", "name", "last_name", "active"])
            driver = existing
        else:
            driver = Driver(
                steam_id=steam_id,
                name=name,
                last_name=request.data.get("last_name", ""),
                country=request.data.get("country", ""),
                active=True,
            )
            driver.set_password(password)
            driver.save()

        refresh = RefreshToken()
        refresh["driver_id"] = driver.id
        refresh["steam_id"] = driver.steam_id
        refresh["driver_name"] = driver.name

        access = refresh.access_token
        access["driver_id"] = driver.id
        access["steam_id"] = driver.steam_id
        access["driver_name"] = driver.name

        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
                "driver": {
                    "id": driver.id,
                    "steam_id": driver.steam_id,
                    "name": driver.name,
                    "last_name": driver.last_name,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class DriverProfileView(APIView):
    """Vista para obtener perfil del driver autenticado"""

    authentication_classes = [DriverJWTAuthentication]
    permission_classes = []

    def get(self, request):
        if not request.user.is_authenticated or not hasattr(request.user, "driver_id"):
            return Response(
                {"error": "No autenticado como driver"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            driver = Driver.objects.select_related("team").get(
                id=request.user.driver_id
            )
            data = {
                "id": driver.id,
                "steam_id": driver.steam_id,
                "name": driver.name,
                "last_name": driver.last_name,
                "number": driver.number,
                "country": driver.country,
                "birth_date": driver.birth_date,
                "team": (
                    {
                        "id": driver.team.id if driver.team else None,
                        "name": driver.team.name if driver.team else None,
                    }
                    if driver.team
                    else None
                ),
                "active": driver.active,
            }
            return Response(data)
        except Driver.DoesNotExist:
            return Response(
                {"error": "Driver no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
