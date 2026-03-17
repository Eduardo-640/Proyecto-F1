from django.contrib import admin
from .models import Temporada


@admin.register(Temporada)
class TemporadaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'año', 'activa', 'creada_en']
    list_filter = ['activa', 'año']
