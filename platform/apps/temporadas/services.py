from django.db.models import Sum
from apps.equipos.models import Equipo
from apps.carreras.models import ResultadoCarrera


def clasificacion_campeonato(temporada_id: int) -> list[dict]:
    """
    Devuelve la clasificación del campeonato de una temporada,
    ordenada por puntos totales de carrera.
    Puntos = suma de posiciones invertidas (1º → más puntos).
    """
    resultados = (
        ResultadoCarrera.objects
        .filter(carrera__temporada_id=temporada_id)
        .values('equipo__id', 'equipo__nombre')
        .annotate(total_creditos=Sum('creditos_otorgados'))
        .order_by('-total_creditos')
    )

    clasificacion = []
    for pos, r in enumerate(resultados, start=1):
        clasificacion.append({
            'posicion': pos,
            'equipo_id': r['equipo__id'],
            'equipo': r['equipo__nombre'],
            'total_creditos': r['total_creditos'] or 0,
        })
    return clasificacion
