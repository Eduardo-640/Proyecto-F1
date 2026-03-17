"""
Tabla de recompensas y lógica de negocio para carreras.
Toda la lógica está aquí; las vistas solo llaman a estas funciones.
"""
from django.db import transaction

from apps.equipos.models import Equipo
from .models import Carrera, EstadoCarrera, ResultadoCarrera, TransaccionCreditos

# ─── Tablas de recompensas (extraídas del TODO) ─────────────────────────────
CREDITOS_POSICION = {1: 200, 2: 170, 3: 150, 4: 120, 5: 100}
CREDITOS_DEFAULT = 80  # para posiciones fuera de tabla

BONUS_POLE = 40
BONUS_VUELTA_RAPIDA = 30
BONUS_TERMINAR = 20

# Bonus de balance: según posición en el campeonato (1.º = 0, etc.)
BONUS_BALANCE_CAMPEONATO = {1: 0, 2: 20, 3: 40, 4: 60, 5: 80}
BONUS_BALANCE_DEFAULT = 100


# ─── Funciones públicas ──────────────────────────────────────────────────────

def calcular_creditos_resultado(
    posicion: int,
    pole: bool = False,
    vuelta_rapida: bool = False,
    termino: bool = True,
) -> int:
    """Calcula los créditos que corresponden a un resultado individual."""
    total = CREDITOS_POSICION.get(posicion, CREDITOS_DEFAULT)
    if pole:
        total += BONUS_POLE
    if vuelta_rapida:
        total += BONUS_VUELTA_RAPIDA
    if termino:
        total += BONUS_TERMINAR
    return total


def calcular_bonus_balance(posicion_campeonato: int) -> int:
    """Devuelve el bonus de balance competitivo según posición en el campeonato."""
    return BONUS_BALANCE_CAMPEONATO.get(posicion_campeonato, BONUS_BALANCE_DEFAULT)


@transaction.atomic
def procesar_resultados_carrera(carrera_id: int, resultados: list[dict]) -> list[ResultadoCarrera]:
    """
    Procesa los resultados de una carrera, asigna créditos y registra transacciones.

    Parámetro `resultados`: lista de dicts con las claves:
        - equipo_id (int)
        - posicion (int)
        - pole (bool, opcional)
        - vuelta_rapida (bool, opcional)
        - termino_carrera (bool, opcional, default True)
        - posicion_campeonato (int, opcional) → para el bonus de balance

    Devuelve la lista de ResultadoCarrera creados.
    """
    carrera = Carrera.objects.select_for_update().get(pk=carrera_id)

    if carrera.estado == EstadoCarrera.FINALIZADA:
        raise ValueError("Esta carrera ya ha sido procesada.")

    registros = []
    for r in resultados:
        equipo = Equipo.objects.select_for_update().get(pk=r['equipo_id'])
        posicion = r['posicion']
        pole = r.get('pole', False)
        vuelta_rapida = r.get('vuelta_rapida', False)
        termino = r.get('termino_carrera', True)
        pos_campeonato = r.get('posicion_campeonato', None)

        creditos = calcular_creditos_resultado(posicion, pole, vuelta_rapida, termino)

        resultado = ResultadoCarrera.objects.create(
            carrera=carrera,
            equipo=equipo,
            posicion=posicion,
            pole=pole,
            vuelta_rapida=vuelta_rapida,
            termino_carrera=termino,
            creditos_otorgados=creditos,
        )

        # Asignar créditos al equipo
        equipo.creditos += creditos
        partes = [f"P{posicion}"]
        if pole:
            partes.append("pole")
        if vuelta_rapida:
            partes.append("vuelta rápida")
        if termino:
            partes.append("finalizó")

        TransaccionCreditos.objects.create(
            equipo=equipo,
            cantidad=creditos,
            tipo=TransaccionCreditos.Tipo.CARRERA,
            descripcion=f"Ronda {carrera.numero_ronda} – {', '.join(partes)}",
            carrera=carrera,
        )

        # Bonus de balance competitivo
        if pos_campeonato is not None:
            bonus = calcular_bonus_balance(pos_campeonato)
            if bonus > 0:
                equipo.creditos += bonus
                TransaccionCreditos.objects.create(
                    equipo=equipo,
                    cantidad=bonus,
                    tipo=TransaccionCreditos.Tipo.BONUS_BALANCE,
                    descripcion=f"Bonus balance – posición {pos_campeonato}º en campeonato",
                    carrera=carrera,
                )

        equipo.save(update_fields=['creditos'])
        registros.append(resultado)

    carrera.estado = EstadoCarrera.FINALIZADA
    carrera.save(update_fields=['estado'])

    return registros
