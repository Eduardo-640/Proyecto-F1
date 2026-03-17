"""
Lógica de negocio para el sistema de desarrollo del coche.
"""
from django.db import transaction

from apps.equipos.models import Equipo
from apps.carreras.models import TransaccionCreditos
from .models import DesarrolloEquipo, MejoraComprada

# ─── Costes de mejora (nivel_actual → nivel_siguiente) ──────────────────────
COSTE_MEJORA = {1: 150, 2: 300, 3: 600, 4: 1000}

# ─── Efectos de motor (nivel → restrictor) ──────────────────────────────────
RESTRICTOR_POR_NIVEL = {1: 5, 2: 4, 3: 3, 4: 2, 5: 0}

# ─── Efectos de aerodinámica (nivel → ballast kg) ───────────────────────────
BALLAST_POR_NIVEL = {1: 40, 2: 30, 3: 20, 4: 10, 5: 0}


# ─── Consultas ───────────────────────────────────────────────────────────────

def obtener_o_crear_desarrollo(equipo_id: int, temporada_id: int) -> DesarrolloEquipo:
    desarrollo, _ = DesarrolloEquipo.objects.get_or_create(
        equipo_id=equipo_id,
        temporada_id=temporada_id,
    )
    return desarrollo


def coste_siguiente_mejora(nivel_actual: int) -> int | None:
    """Devuelve el coste de subir al siguiente nivel, o None si ya está al máximo."""
    return COSTE_MEJORA.get(nivel_actual)


def puede_comprar(equipo: Equipo, nivel_actual: int) -> tuple[bool, str]:
    coste = coste_siguiente_mejora(nivel_actual)
    if coste is None:
        return False, "El departamento ya está al nivel máximo."
    if equipo.creditos < coste:
        return False, f"Créditos insuficientes. Necesitas {coste}, tienes {equipo.creditos}."
    return True, ""


# ─── Compra de mejora ────────────────────────────────────────────────────────

@transaction.atomic
def comprar_mejora(equipo_id: int, temporada_id: int, departamento: str) -> MejoraComprada:
    """
    Compra una mejora para el departamento indicado.
    La mejora queda marcada como `aplicada=False` hasta el próximo evento.
    """
    equipo = Equipo.objects.select_for_update().get(pk=equipo_id)
    desarrollo = DesarrolloEquipo.objects.select_for_update().get(
        equipo_id=equipo_id, temporada_id=temporada_id
    )

    nivel_actual = desarrollo.nivel(departamento)
    ok, motivo = puede_comprar(equipo, nivel_actual)
    if not ok:
        raise ValueError(motivo)

    coste = COSTE_MEJORA[nivel_actual]
    nivel_nuevo = nivel_actual + 1

    # Descontar créditos
    equipo.creditos -= coste
    equipo.save(update_fields=['creditos'])

    # Registrar transacción
    TransaccionCreditos.objects.create(
        equipo=equipo,
        cantidad=-coste,
        tipo=TransaccionCreditos.Tipo.COMPRA_MEJORA,
        descripcion=f"Mejora {departamento} nivel {nivel_actual}→{nivel_nuevo}",
    )

    # Crear registro de mejora (pendiente de aplicar)
    mejora = MejoraComprada.objects.create(
        equipo=equipo,
        temporada_id=temporada_id,
        departamento=departamento,
        nivel_anterior=nivel_actual,
        nivel_nuevo=nivel_nuevo,
        coste=coste,
        aplicada=False,
    )
    return mejora


@transaction.atomic
def aplicar_mejoras_pendientes(equipo_id: int, temporada_id: int) -> list[MejoraComprada]:
    """
    Aplica todas las mejoras pendientes de un equipo en la temporada.
    Se llama antes del siguiente evento de carrera.
    """
    mejoras_pendientes = MejoraComprada.objects.select_for_update().filter(
        equipo_id=equipo_id,
        temporada_id=temporada_id,
        aplicada=False,
    ).order_by('comprada_en')

    desarrollo = DesarrolloEquipo.objects.select_for_update().get(
        equipo_id=equipo_id, temporada_id=temporada_id
    )

    aplicadas = []
    for mejora in mejoras_pendientes:
        setattr(desarrollo, mejora.departamento, mejora.nivel_nuevo)
        mejora.aplicada = True
        mejora.save(update_fields=['aplicada'])
        aplicadas.append(mejora)

    desarrollo.save()
    return aplicadas


# ─── Parámetros AC ───────────────────────────────────────────────────────────

def parametros_coche(desarrollo: DesarrolloEquipo) -> dict:
    """
    Devuelve los parámetros de Assetto Corsa (restrictor y ballast)
    calculados a partir del nivel de desarrollo actual.
    """
    return {
        'restrictor': RESTRICTOR_POR_NIVEL[desarrollo.motor],
        'ballast': BALLAST_POR_NIVEL[desarrollo.aerodinamica],
        'motor': desarrollo.motor,
        'aerodinamica': desarrollo.aerodinamica,
        'chasis': desarrollo.chasis,
        'suspension': desarrollo.suspension,
        'electronica': desarrollo.electronica,
    }
