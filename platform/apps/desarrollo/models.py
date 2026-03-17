from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.equipos.models import Equipo
from apps.temporadas.models import Temporada

NIVEL_MIN = 1
NIVEL_MAX = 5
nivel_field = lambda: models.PositiveSmallIntegerField(  # noqa: E731
    default=1,
    validators=[MinValueValidator(NIVEL_MIN), MaxValueValidator(NIVEL_MAX)],
)


class DesarrolloEquipo(models.Model):
    """Estado actual del desarrollo técnico de un equipo en una temporada."""

    equipo = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name='desarrollos'
    )
    temporada = models.ForeignKey(
        Temporada, on_delete=models.CASCADE, related_name='desarrollos'
    )

    motor = nivel_field()
    aerodinamica = nivel_field()
    chasis = nivel_field()
    suspension = nivel_field()
    electronica = nivel_field()

    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('equipo', 'temporada')]
        verbose_name = 'Desarrollo del equipo'
        verbose_name_plural = 'Desarrollos de los equipos'

    def __str__(self):
        return f"{self.equipo} – {self.temporada}"

    def nivel(self, departamento: str) -> int:
        return getattr(self, departamento)


class MejoraComprada(models.Model):
    """Historial de mejoras adquiridas por un equipo."""

    class Departamento(models.TextChoices):
        MOTOR = 'motor', 'Motor'
        AERODINAMICA = 'aerodinamica', 'Aerodinámica'
        CHASIS = 'chasis', 'Chasis'
        SUSPENSION = 'suspension', 'Suspensión'
        ELECTRONICA = 'electronica', 'Electrónica'

    equipo = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name='mejoras'
    )
    temporada = models.ForeignKey(
        Temporada, on_delete=models.CASCADE, related_name='mejoras'
    )
    departamento = models.CharField(max_length=20, choices=Departamento.choices)
    nivel_anterior = models.PositiveSmallIntegerField()
    nivel_nuevo = models.PositiveSmallIntegerField()
    coste = models.PositiveIntegerField()
    aplicada = models.BooleanField(default=False)
    comprada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-comprada_en']
        verbose_name = 'Mejora comprada'
        verbose_name_plural = 'Mejoras compradas'

    def __str__(self):
        return f"{self.equipo} – {self.get_departamento_display()} {self.nivel_anterior}→{self.nivel_nuevo}"
