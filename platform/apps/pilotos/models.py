from django.db import models
from apps.equipos.models import Equipo


class Piloto(models.Model):
    nombre = models.CharField(max_length=100)
    equipo = models.OneToOneField(
        Equipo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='piloto',
    )
    steam_id = models.CharField(max_length=64, blank=True, null=True, unique=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Piloto'
        verbose_name_plural = 'Pilotos'

    def __str__(self):
        return self.nombre
