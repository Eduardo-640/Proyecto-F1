from django.db import models


class Equipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    creditos = models.PositiveIntegerField(default=500)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creditos']
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return self.nombre
