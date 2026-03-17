from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Carrera, ResultadoCarrera, TransaccionCreditos
from .serializers import (
    CarreraSerializer,
    ResultadoCarreraSerializer,
    ProcesarResultadosSerializer,
    TransaccionCreditosSerializer,
)
from .services import procesar_resultados_carrera


class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.select_related('temporada').all()
    serializer_class = CarreraSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], url_path='procesar_resultados')
    def procesar_resultados(self, request, pk=None):
        """
        POST /api/carreras/{id}/procesar_resultados/
        Body: lista de resultados por equipo.
        """
        serializer = ProcesarResultadosSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        try:
            resultados = procesar_resultados_carrera(
                carrera_id=pk,
                resultados=serializer.validated_data,
            )
        except (ValueError, Carrera.DoesNotExist) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ResultadoCarreraSerializer(resultados, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['get'], url_path='resultados')
    def resultados(self, request, pk=None):
        """GET /api/carreras/{id}/resultados/"""
        qs = ResultadoCarrera.objects.filter(carrera_id=pk).select_related('equipo')
        return Response(ResultadoCarreraSerializer(qs, many=True).data)


class TransaccionCreditosViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TransaccionCreditos.objects.select_related('equipo', 'carrera').all()
    serializer_class = TransaccionCreditosSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        equipo_id = self.request.query_params.get('equipo')
        if equipo_id:
            qs = qs.filter(equipo_id=equipo_id)
        return qs
