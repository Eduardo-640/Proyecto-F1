from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Race, RaceResult
from .services.analytics import (
    build_driver_stats,
    build_race_metrics,
    build_race_timeline,
    build_team_stats,
)


class CarreraListView(View):
    def get(self, request):
        carreras = Race.objects.select_related('season', 'circuit').all()
        
        data = [
            {
                'id': c.id,
                'nombre': f"Ronda {c.round_number} - {c.circuit.name if c.circuit else 'Carrera'}",
                'numero_ronda': c.round_number,
                'circuito': c.circuit.name if c.circuit else None,
                'fecha_carrera': c.race_date,
                'estado': c.status,
                'temporada': c.season.year if c.season else None,
            }
            for c in carreras
        ]
        
        return JsonResponse(data, safe=False)


class RaceMetricsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk: int):
        try:
            payload = build_race_metrics(pk)
        except Race.DoesNotExist:
            return Response({"detail": "Carrera no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except RaceResult.DoesNotExist as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(payload)


class RaceTimelineView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk: int):
        try:
            data = build_race_timeline(pk)
        except Race.DoesNotExist:
            return Response({"detail": "Carrera no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)


class DriverStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk: int):
        race_id = request.query_params.get("race")
        if not race_id:
            return Response(
                {"detail": "El parámetro 'race' es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            race_id_int = int(race_id)
        except ValueError:
            return Response(
                {"detail": "El parámetro 'race' debe ser numérico"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = build_driver_stats(pk, race_id_int)
        except Race.DoesNotExist:
            return Response({"detail": "Carrera no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except RaceResult.DoesNotExist as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)


class TeamStatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk: int):
        try:
            team_id = int(pk)
        except (TypeError, ValueError):
            return Response({"detail": "Team ID inválido"}, status=status.HTTP_400_BAD_REQUEST)
        race_id = request.query_params.get("race")
        if not race_id:
            return Response(
                {"detail": "El parámetro 'race' es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            race_id_int = int(race_id)
        except ValueError:
            return Response(
                {"detail": "El parámetro 'race' debe ser numérico"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = build_team_stats(team_id, race_id_int)
        except Race.DoesNotExist:
            return Response({"detail": "Carrera no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        except RaceResult.DoesNotExist as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(data)
