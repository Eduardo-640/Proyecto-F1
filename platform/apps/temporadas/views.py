from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Temporada
from .serializers import TemporadaSerializer
from .services import clasificacion_campeonato


class TemporadaViewSet(viewsets.ModelViewSet):
    queryset = Temporada.objects.all()
    serializer_class = TemporadaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['get'], url_path='clasificacion')
    def clasificacion(self, request, pk=None):
        """GET /api/temporadas/{id}/clasificacion/ — clasificación del campeonato."""
        data = clasificacion_campeonato(temporada_id=pk)
        return Response(data)
