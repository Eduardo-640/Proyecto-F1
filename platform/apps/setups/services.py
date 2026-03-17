"""
Orquesta los generators con datos de la base de datos.
"""
from apps.carreras.models import Carrera
from apps.pilotos.models import Piloto
from apps.desarrollo.services import obtener_o_crear_desarrollo
from .generators import generar_entry_list, generar_setup_equipo

MODELO_COCHE_DEFAULT = 'rss_formula_rss_3'


def entry_list_para_carrera(carrera_id: int, modelo_coche: str = MODELO_COCHE_DEFAULT) -> str:
    """
    Genera entry_list.ini para todos los pilotos activos en la carrera.
    Requiere que cada piloto tenga un steam_id y un equipo asignado.
    """
    carrera = Carrera.objects.select_related('temporada').get(pk=carrera_id)
    pilotos = Piloto.objects.filter(activo=True).select_related('equipo').order_by('id')

    entradas = []
    for idx, piloto in enumerate(pilotos):
        if not piloto.equipo or not piloto.steam_id:
            continue
        desarrollo = obtener_o_crear_desarrollo(piloto.equipo_id, carrera.temporada_id)
        entradas.append({
            'index': idx,
            'modelo': modelo_coche,
            'guid': piloto.steam_id,
            'restrictor': 5 - (desarrollo.motor - 1),   # nivel 1→5, nivel 5→0
            'ballast': max(0, 40 - (desarrollo.aerodinamica - 1) * 10),
            'equipo': piloto.equipo.nombre,
        })

    return generar_entry_list(entradas)


def setups_para_carrera(carrera_id: int) -> dict[str, str]:
    """
    Devuelve un dict { nombre_archivo: contenido_ini }
    con un setup por equipo activo.
    """
    carrera = Carrera.objects.select_related('temporada').get(pk=carrera_id)
    pilotos = Piloto.objects.filter(activo=True).select_related('equipo').order_by('id')

    resultado = {}
    for piloto in pilotos:
        if not piloto.equipo:
            continue
        desarrollo = obtener_o_crear_desarrollo(piloto.equipo_id, carrera.temporada_id)
        nombre = f"{piloto.equipo.nombre.lower().replace(' ', '_')}_{carrera.circuito.lower().replace(' ', '_')}.ini"
        resultado[nombre] = generar_setup_equipo(
            nombre_equipo=piloto.equipo.nombre,
            nivel_motor=desarrollo.motor,
            nivel_aerodinamica=desarrollo.aerodinamica,
            nivel_chasis=desarrollo.chasis,
            nivel_suspension=desarrollo.suspension,
            nivel_electronica=desarrollo.electronica,
        )
    return resultado
