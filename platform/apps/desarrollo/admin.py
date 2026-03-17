from django.contrib import admin
from .models import DesarrolloEquipo, MejoraComprada


@admin.register(DesarrolloEquipo)
class DesarrolloEquipoAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'temporada', 'motor', 'aerodinamica', 'chasis', 'suspension', 'electronica', 'actualizado_en']
    list_filter = ['temporada']
    search_fields = ['equipo__nombre']


@admin.register(MejoraComprada)
class MejoraCompradaAdmin(admin.ModelAdmin):
    list_display = ['equipo', 'departamento', 'nivel_anterior', 'nivel_nuevo', 'coste', 'aplicada', 'comprada_en']
    list_filter = ['aplicada', 'departamento', 'temporada']
    search_fields = ['equipo__nombre']
