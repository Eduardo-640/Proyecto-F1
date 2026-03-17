"""
Generadores de archivos .ini para Assetto Corsa.
Pura lógica, sin acceso a base de datos.
"""
import configparser
import io

# ─── Mapeados de desarrollo a parámetros AC ─────────────────────────────────
RESTRICTOR_POR_NIVEL = {1: 5, 2: 4, 3: 3, 4: 2, 5: 0}
BALLAST_POR_NIVEL = {1: 40, 2: 30, 3: 20, 4: 10, 5: 0}

# Parámetros de setup por nivel de chasis/suspensión/electrónica
# (valores de ejemplo; ajustar según el coche)
CHASIS_SETUP = {
    1: {'ARB_FRONT': '1', 'ARB_REAR': '1'},
    2: {'ARB_FRONT': '2', 'ARB_REAR': '1'},
    3: {'ARB_FRONT': '2', 'ARB_REAR': '2'},
    4: {'ARB_FRONT': '3', 'ARB_REAR': '2'},
    5: {'ARB_FRONT': '3', 'ARB_REAR': '3'},
}

SUSPENSION_SETUP = {
    1: {'SPRING_RATE_F': '160000', 'SPRING_RATE_R': '120000', 'CAMBER_F': '-2.0', 'TOE_F': '0.0'},
    2: {'SPRING_RATE_F': '155000', 'SPRING_RATE_R': '115000', 'CAMBER_F': '-2.5', 'TOE_F': '-0.05'},
    3: {'SPRING_RATE_F': '150000', 'SPRING_RATE_R': '110000', 'CAMBER_F': '-3.0', 'TOE_F': '-0.1'},
    4: {'SPRING_RATE_F': '145000', 'SPRING_RATE_R': '105000', 'CAMBER_F': '-3.2', 'TOE_F': '-0.1'},
    5: {'SPRING_RATE_F': '140000', 'SPRING_RATE_R': '100000', 'CAMBER_F': '-3.5', 'TOE_F': '-0.15'},
}

ELECTRONICA_SETUP = {
    1: {'DIFF_POWER': '30', 'DIFF_COAST': '20', 'TC': '3'},
    2: {'DIFF_POWER': '40', 'DIFF_COAST': '25', 'TC': '2'},
    3: {'DIFF_POWER': '50', 'DIFF_COAST': '30', 'TC': '2'},
    4: {'DIFF_POWER': '60', 'DIFF_COAST': '35', 'TC': '1'},
    5: {'DIFF_POWER': '70', 'DIFF_COAST': '40', 'TC': '0'},
}


# ─── entry_list.ini ──────────────────────────────────────────────────────────

def generar_entry_list(entradas: list[dict]) -> str:
    """
    Genera el contenido de entry_list.ini a partir de una lista de dicts:
        [
          {
            'index': 0,
            'modelo': 'rss_formula_rss_3',
            'guid': '765611900000000',
            'restrictor': 5,
            'ballast': 40,
            'equipo': 'Equipo Alpha',
          },
          ...
        ]
    Devuelve el string listo para escribir en disco.
    """
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str  # preservar mayúsculas

    for e in entradas:
        section = f"CAR_{e['index']}"
        cfg[section] = {
            'MODEL': e['modelo'],
            'GUID': e['guid'],
            'BALLAST': str(e['ballast']),
            'RESTRICTOR': str(e['restrictor']),
            'TEAM': e.get('equipo', ''),
        }

    buf = io.StringIO()
    cfg.write(buf)
    return buf.getvalue()


# ─── Setup individual de equipo ──────────────────────────────────────────────

def generar_setup_equipo(
    nombre_equipo: str,
    nivel_motor: int,
    nivel_aerodinamica: int,
    nivel_chasis: int,
    nivel_suspension: int,
    nivel_electronica: int,
) -> str:
    """
    Genera el preset de setup .ini para un equipo concreto.
    Devuelve el string del archivo.
    """
    cfg = configparser.RawConfigParser()
    cfg.optionxform = str

    cfg['INFO'] = {'EQUIPO': nombre_equipo}

    cfg['AERO'] = {
        'BALLAST': str(BALLAST_POR_NIVEL[nivel_aerodinamica]),
        'RESTRICTOR': str(RESTRICTOR_POR_NIVEL[nivel_motor]),
    }

    cfg['ARB'] = CHASIS_SETUP[nivel_chasis]
    cfg['SUSPENSION'] = SUSPENSION_SETUP[nivel_suspension]
    cfg['ELECTRONICS'] = ELECTRONICA_SETUP[nivel_electronica]

    buf = io.StringIO()
    cfg.write(buf)
    return buf.getvalue()
