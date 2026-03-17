from rest_framework import serializers
from .models import DesarrolloEquipo, MejoraComprada


class DesarrolloEquipoSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)

    class Meta:
        model = DesarrolloEquipo
        fields = [
            'id', 'equipo', 'equipo_nombre', 'temporada',
            'motor', 'aerodinamica', 'chasis', 'suspension', 'electronica',
            'actualizado_en',
        ]
        read_only_fields = ['actualizado_en']


class MejoraCompradaSerializer(serializers.ModelSerializer):
    departamento_display = serializers.CharField(source='get_departamento_display', read_only=True)

    class Meta:
        model = MejoraComprada
        fields = [
            'id', 'equipo', 'temporada', 'departamento', 'departamento_display',
            'nivel_anterior', 'nivel_nuevo', 'coste', 'aplicada', 'comprada_en',
        ]
        read_only_fields = ['nivel_anterior', 'nivel_nuevo', 'coste', 'aplicada', 'comprada_en']


class ComprarMejoraSerializer(serializers.Serializer):
    """Payload para POST /api/desarrollo/{equipo_id}/mejora/"""
    temporada_id = serializers.IntegerField()
    departamento = serializers.ChoiceField(choices=MejoraComprada.Departamento.choices)
