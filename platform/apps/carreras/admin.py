from django.contrib import admin
from .models import Carrera, ResultadoCarrera, TransaccionCreditos


@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'temporada', 'numero_ronda', 'circuito', 'estado', 'fecha_carrera']
    list_filter = ['temporada', 'estado']
    search_fields = ['circuito']


class ResultadoInline(admin.TabularInline):
    model = ResultadoCarrera
    extra = 0
    readonly_fields = ['creditos_otorgados']


@admin.register(ResultadoCarrera)
class ResultadoCarreraAdmin(admin.ModelAdmin):
    list_display = ['carrera', 'equipo', 'posicion', 'pole', 'vuelta_rapida', 'creditos_otorgados']
    list_filter = ['carrera__temporada', 'carrera']


@admin.register(TransaccionCreditos)
class TransaccionCreditosAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'cantidad', 'tipo', 'descripcion', 'creada_en']
    list_filter = ['tipo', 'equipo']
    readonly_fields = ['creada_en']
