from rest_framework import serializers
from apps.equipos.serializers import EquipoResumenSerializer
from .models import Piloto


class PilotoSerializer(serializers.ModelSerializer):
    equipo_detalle = EquipoResumenSerializer(source='equipo', read_only=True)

    class Meta:
        model = Piloto
        fields = ['id', 'nombre', 'equipo', 'equipo_detalle', 'steam_id', 'activo', 'creado_en']
        read_only_fields = ['creado_en']
