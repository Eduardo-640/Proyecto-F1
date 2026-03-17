from django.db import models


class Temporada(models.Model):
    nombre = models.CharField(max_length=100)
    año = models.PositiveSmallIntegerField()
    activa = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-año']
        verbose_name = 'Temporada'
        verbose_name_plural = 'Temporadas'

    def __str__(self):
        return f"{self.nombre} ({self.año})"
