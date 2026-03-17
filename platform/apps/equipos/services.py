from django.db import transaction
from .models import Equipo


def ajustar_creditos(equipo: Equipo, cantidad: int, descripcion: str = '') -> Equipo:
    """Suma o resta créditos a un equipo de forma atómica."""
    with transaction.atomic():
        equipo = Equipo.objects.select_for_update().get(pk=equipo.pk)
        equipo.creditos = max(0, equipo.creditos + cantidad)
        equipo.save(update_fields=['creditos'])
    return equipo
