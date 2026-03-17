from django.contrib import admin
from .models import Piloto


@admin.register(Piloto)
class PilotoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'equipo', 'steam_id', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'steam_id']
