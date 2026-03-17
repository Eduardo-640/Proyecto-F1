from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DesarrolloEquipo, MejoraComprada
from .serializers import (
    DesarrolloEquipoSerializer,
    MejoraCompradaSerializer,
    ComprarMejoraSerializer,
)
from .services import (
    obtener_o_crear_desarrollo,
    comprar_mejora,
    aplicar_mejoras_pendientes,
    parametros_coche,
)


class DesarrolloEquipoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DesarrolloEquipo.objects.select_related('equipo', 'temporada').all()
    serializer_class = DesarrolloEquipoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'], url_path=r'equipo/(?P<equipo_id>\d+)/temporada/(?P<temporada_id>\d+)')
    def por_equipo_temporada(self, request, equipo_id=None, temporada_id=None):
        """GET /api/desarrollo/equipo/{equipo_id}/temporada/{temporada_id}/"""
        desarrollo = obtener_o_crear_desarrollo(equipo_id, temporada_id)
        return Response(DesarrolloEquipoSerializer(desarrollo).data)

    @action(
        detail=False,
        methods=['post'],
        url_path=r'equipo/(?P<equipo_id>\d+)/mejora',
        permission_classes=[permissions.IsAuthenticated],
    )
    def comprar(self, request, equipo_id=None):
        """POST /api/desarrollo/equipo/{equipo_id}/mejora"""
        serializer = ComprarMejoraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            mejora = comprar_mejora(
                equipo_id=equipo_id,
                temporada_id=serializer.validated_data['temporada_id'],
                departamento=serializer.validated_data['departamento'],
            )
        except (ValueError, DesarrolloEquipo.DoesNotExist) as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(MejoraCompradaSerializer(mejora).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['post'],
        url_path=r'equipo/(?P<equipo_id>\d+)/temporada/(?P<temporada_id>\d+)/aplicar',
        permission_classes=[permissions.IsAuthenticated],
    )
    def aplicar(self, request, equipo_id=None, temporada_id=None):
        """POST /api/desarrollo/equipo/{equipo_id}/temporada/{temporada_id}/aplicar"""
        aplicadas = aplicar_mejoras_pendientes(equipo_id, temporada_id)
        return Response(MejoraCompradaSerializer(aplicadas, many=True).data)

    @action(
        detail=False,
        methods=['get'],
        url_path=r'equipo/(?P<equipo_id>\d+)/temporada/(?P<temporada_id>\d+)/parametros',
    )
    def parametros(self, request, equipo_id=None, temporada_id=None):
        """GET /api/desarrollo/equipo/{equipo_id}/temporada/{temporada_id}/parametros"""
        desarrollo = obtener_o_crear_desarrollo(equipo_id, temporada_id)
        return Response(parametros_coche(desarrollo))
