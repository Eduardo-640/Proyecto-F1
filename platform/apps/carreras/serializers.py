from rest_framework import serializers
from .models import Carrera, ResultadoCarrera, TransaccionCreditos


class CarreraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrera
        fields = ['id', 'temporada', 'numero_ronda', 'circuito', 'fecha_carrera', 'estado']


class ResultadoCarreraSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)

    class Meta:
        model = ResultadoCarrera
        fields = [
            'id', 'carrera', 'equipo', 'equipo_nombre',
            'posicion', 'pole', 'vuelta_rapida', 'termino_carrera', 'creditos_otorgados',
        ]
        read_only_fields = ['creditos_otorgados']


class ProcesarResultadosSerializer(serializers.Serializer):
    """Payload para POST /api/carreras/{id}/procesar_resultados/"""
    equipo_id = serializers.IntegerField()
    posicion = serializers.IntegerField(min_value=1)
    pole = serializers.BooleanField(default=False)
    vuelta_rapida = serializers.BooleanField(default=False)
    termino_carrera = serializers.BooleanField(default=True)
    posicion_campeonato = serializers.IntegerField(min_value=1, required=False)


class TransaccionCreditosSerializer(serializers.ModelSerializer):
    equipo_nombre = serializers.CharField(source='equipo.nombre', read_only=True)

    class Meta:
        model = TransaccionCreditos
        fields = ['id', 'equipo', 'equipo_nombre', 'cantidad', 'tipo', 'descripcion', 'carrera', 'creada_en']
        read_only_fields = ['creada_en']
