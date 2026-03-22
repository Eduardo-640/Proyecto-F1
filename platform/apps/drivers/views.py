from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Driver
from apps.teams.models import Team
from apps.races.models import Race
from apps.seasons.models import Season
from .permissions import IsDriverAuthenticated, IsDriverOwner


# Vistas Públicas (sin autenticación requerida)
class DriverListPublicView(APIView):
    """Lista pública de drivers - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request):
        drivers = Driver.objects.select_related('team').filter(active=True)
        data = [{
            'id': driver.id,
            'steam_id': driver.steam_id,
            'name': driver.name,
            'last_name': driver.last_name,
            'number': driver.number,
            'country': driver.country,
            'team': driver.team.name if driver.team else None,
        } for driver in drivers]

        return Response(data)


class DriverDetailPublicView(APIView):
    """Detalle público de un driver - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        driver = get_object_or_404(Driver.objects.select_related('team'), pk=pk, active=True)
        data = {
            'id': driver.id,
            'steam_id': driver.steam_id,
            'name': driver.name,
            'last_name': driver.last_name,
            'number': driver.number,
            'country': driver.country,
            'birth_date': driver.birth_date,
            'team': {
                'id': driver.team.id if driver.team else None,
                'name': driver.team.name if driver.team else None,
            } if driver.team else None,
        }
        return Response(data)


class TeamListPublicView(APIView):
    """Lista pública de equipos - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request):
        teams = Team.objects.prefetch_related('drivers').all()
        data = [{
            'id': team.id,
            'name': team.name,
            'country': team.country,
            'drivers': [{
                'id': driver.id,
                'name': f"{driver.name} {driver.last_name}",
                'number': driver.number,
            } for driver in team.drivers.filter(active=True)]
        } for team in teams]

        return Response(data)


class TeamDetailPublicView(APIView):
    """Detalle público de un equipo - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        team = get_object_or_404(Team.objects.prefetch_related('drivers'), pk=pk)
        data = {
            'id': team.id,
            'name': team.name,
            'country': team.country,
            'drivers': [{
                'id': driver.id,
                'name': f"{driver.name} {driver.last_name}",
                'number': driver.number,
            } for driver in team.drivers.filter(active=True)]
        }
        return Response(data)


class RaceListPublicView(APIView):
    """Lista pública de carreras - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request):
        races = Race.objects.select_related('season').all()
        data = [{
            'id': race.id,
            'name': race.name,
            'country': race.country,
            'date': race.date,
            'season': race.season.year if race.season else None,
        } for race in races]

        return Response(data)


class RaceDetailPublicView(APIView):
    """Detalle público de una carrera - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        race = get_object_or_404(Race.objects.select_related('season'), pk=pk)
        data = {
            'id': race.id,
            'name': race.name,
            'country': race.country,
            'date': race.date,
            'season': {
                'id': race.season.id if race.season else None,
                'year': race.season.year if race.season else None,
            } if race.season else None,
        }
        return Response(data)


class SeasonListPublicView(APIView):
    """Lista pública de temporadas - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request):
        seasons = Season.objects.prefetch_related('races').all()
        data = [{
            'id': season.id,
            'year': season.year,
            'races_count': season.races.count(),
        } for season in seasons]

        return Response(data)


class SeasonDetailPublicView(APIView):
    """Detalle público de una temporada - acceso sin autenticación"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        season = get_object_or_404(Season.objects.prefetch_related('races'), pk=pk)
        data = {
            'id': season.id,
            'year': season.year,
            'races': [{
                'id': race.id,
                'name': race.name,
                'country': race.country,
                'date': race.date,
            } for race in season.races.all()]
        }
        return Response(data)


# Vistas Protegidas (requieren autenticación de driver)
class DriverListView(APIView):
    """Lista de drivers - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request):
        drivers = Driver.objects.select_related('team').all()
        data = [{
            'id': driver.id,
            'steam_id': driver.steam_id,
            'name': driver.name,
            'last_name': driver.last_name,
            'number': driver.number,
            'country': driver.country,
            'birth_date': driver.birth_date,
            'price': driver.price,
            'team': driver.team.name if driver.team else None,
            'active': driver.active,
        } for driver in drivers]

        return Response(data)


class DriverDetailView(APIView):
    """Detalle de un driver - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request, pk):
        driver = get_object_or_404(Driver.objects.select_related('team'), pk=pk)
        data = {
            'id': driver.id,
            'steam_id': driver.steam_id,
            'name': driver.name,
            'last_name': driver.last_name,
            'number': driver.number,
            'country': driver.country,
            'birth_date': driver.birth_date,
            'price': driver.price,
            'team': {
                'id': driver.team.id if driver.team else None,
                'name': driver.team.name if driver.team else None,
            } if driver.team else None,
            'active': driver.active,
        }
        return Response(data)


class TeamListView(APIView):
    """Lista de equipos - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request):
        teams = Team.objects.prefetch_related('drivers').all()
        data = [{
            'id': team.id,
            'name': team.name,
            'country': team.country,
            'drivers': [{
                'id': driver.id,
                'steam_id': driver.steam_id,
                'name': f"{driver.name} {driver.last_name}",
                'number': driver.number,
                'active': driver.active,
            } for driver in team.drivers.all()]
        } for team in teams]

        return Response(data)


class TeamDetailView(APIView):
    """Detalle de un equipo - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request, pk):
        team = get_object_or_404(Team.objects.prefetch_related('drivers'), pk=pk)
        data = {
            'id': team.id,
            'name': team.name,
            'country': team.country,
            'drivers': [{
                'id': driver.id,
                'steam_id': driver.steam_id,
                'name': f"{driver.name} {driver.last_name}",
                'number': driver.number,
                'active': driver.active,
            } for driver in team.drivers.all()]
        }
        return Response(data)


class RaceListView(APIView):
    """Lista de carreras - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request):
        races = Race.objects.select_related('season').all()
        data = [{
            'id': race.id,
            'name': race.name,
            'country': race.country,
            'date': race.date,
            'season': race.season.year if race.season else None,
        } for race in races]

        return Response(data)


class RaceDetailView(APIView):
    """Detalle de una carrera - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request, pk):
        race = get_object_or_404(Race.objects.select_related('season'), pk=pk)
        data = {
            'id': race.id,
            'name': race.name,
            'country': race.country,
            'date': race.date,
            'season': {
                'id': race.season.id if race.season else None,
                'year': race.season.year if race.season else None,
            } if race.season else None,
        }
        return Response(data)


class SeasonListView(APIView):
    """Lista de temporadas - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request):
        seasons = Season.objects.prefetch_related('races').all()
        data = [{
            'id': season.id,
            'year': season.year,
            'races_count': season.races.count(),
        } for season in seasons]

        return Response(data)


class SeasonDetailView(APIView):
    """Detalle de una temporada - requiere autenticación de driver"""
    permission_classes = [IsDriverAuthenticated]

    def get(self, request, pk):
        season = get_object_or_404(Season.objects.prefetch_related('races'), pk=pk)
        data = {
            'id': season.id,
            'year': season.year,
            'races': [{
                'id': race.id,
                'name': race.name,
                'country': race.country,
                'date': race.date,
            } for race in season.races.all()]
        }
        return Response(data)
