from rest_framework import serializers
from .models import Equipo


class EquipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipo
        fields = ['id', 'nombre', 'creditos', 'activo', 'creado_en']
        read_only_fields = ['creditos', 'creado_en']


class EquipoResumenSerializer(serializers.ModelSerializer):
    """Versión compacta para listas y relaciones."""
    class Meta:
        model = Equipo
        fields = ['id', 'nombre', 'creditos']
