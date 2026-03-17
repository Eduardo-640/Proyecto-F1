from django.contrib import admin
from .models import Equipo


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'creditos', 'activo', 'creado_en']
    list_filter = ['activo']
    search_fields = ['nombre']
