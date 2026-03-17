from rest_framework import serializers
from .models import Temporada


class TemporadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporada
        fields = ['id', 'nombre', 'año', 'activa', 'creada_en']
        read_only_fields = ['creada_en']
