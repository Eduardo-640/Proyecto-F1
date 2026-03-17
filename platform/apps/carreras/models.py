from django.db import models
from apps.temporadas.models import Temporada
from apps.equipos.models import Equipo


class EstadoCarrera(models.TextChoices):
    PRACTICA = 'practica', 'Práctica'
    CLASIFICACION = 'clasificacion', 'Clasificación'
    CARRERA = 'carrera', 'Carrera'
    FINALIZADA = 'finalizada', 'Finalizada'


class Carrera(models.Model):
    temporada = models.ForeignKey(
        Temporada, on_delete=models.CASCADE, related_name='carreras'
    )
    numero_ronda = models.PositiveSmallIntegerField()
    circuito = models.CharField(max_length=100)
    fecha_carrera = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoCarrera.choices,
        default=EstadoCarrera.PRACTICA,
    )

    class Meta:
        ordering = ['temporada', 'numero_ronda']
        unique_together = [('temporada', 'numero_ronda')]
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'

    def __str__(self):
        return f"Ronda {self.numero_ronda} – {self.circuito} ({self.temporada})"


class ResultadoCarrera(models.Model):
    carrera = models.ForeignKey(
        Carrera, on_delete=models.CASCADE, related_name='resultados'
    )
    equipo = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name='resultados'
    )
    posicion = models.PositiveSmallIntegerField()
    pole = models.BooleanField(default=False)
    vuelta_rapida = models.BooleanField(default=False)
    termino_carrera = models.BooleanField(default=True)
    creditos_otorgados = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('carrera', 'equipo')]
        ordering = ['carrera', 'posicion']
        verbose_name = 'Resultado de carrera'
        verbose_name_plural = 'Resultados de carrera'

    def __str__(self):
        return f"{self.equipo} – P{self.posicion} ({self.carrera})"


class TransaccionCreditos(models.Model):
    class Tipo(models.TextChoices):
        CARRERA = 'carrera', 'Resultado de carrera'
        BONUS_BALANCE = 'bonus_balance', 'Bonus de balance competitivo'
        COMPRA_MEJORA = 'compra_mejora', 'Compra de mejora'
        AJUSTE_ADMIN = 'ajuste_admin', 'Ajuste administrativo'

    equipo = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name='transacciones'
    )
    cantidad = models.IntegerField()  # puede ser negativo (gastos)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    descripcion = models.CharField(max_length=255, blank=True)
    carrera = models.ForeignKey(
        Carrera,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones',
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creada_en']
        verbose_name = 'Transacción de créditos'
        verbose_name_plural = 'Transacciones de créditos'

    def __str__(self):
        signo = '+' if self.cantidad >= 0 else ''
        return f"{self.equipo} {signo}{self.cantidad} ({self.get_tipo_display()})"
