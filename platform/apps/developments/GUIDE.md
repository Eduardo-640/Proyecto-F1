# Developments App — Guía de uso

Sistema de desarrollo técnico de equipos para la simulación de Fórmula.  
Mapea los niveles de cada departamento (1–5) a parámetros reales de setup
de Assetto Corsa (`.ini`), con sinergias, énfasis por circuito y bonificaciones
por patrocinador.

---

## Arquitectura en capas

```
Admin / Management Commands
        │
        ▼
  setup_service.py   ←  lógica de negocio (BD + algoritmo)
        │
        ▼
 setup_generator.py  ←  algoritmo puro (sin acceso a BD)
        │
        ▼
  models.py          ←  TeamDevelopment, PurchasedUpgrade,
                         CarSetupSnapshot, CircuitSetup,
                         BalanceOfPerformance, AccionMasiva
```

---

## Modelos principales

| Modelo                 | Descripción                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| `TeamDevelopment`      | Niveles actuales (1–5) por departamento en una temporada                    |
| `PurchasedUpgrade`     | Historial de mejoras compradas                                              |
| `CarSetupSnapshot`     | Snapshot versionado del `.ini` (se crea en v1 y evoluciona con cada mejora) |
| `CircuitSetup`         | Setup de fin de semana adaptado a un circuito específico                    |
| `BalanceOfPerformance` | Lastre y restrictor gestionados por el admin                                |
| `AccionMasiva`         | **Punto de entrada centralizado** para operaciones masivas                  |

---

## AccionMasiva — Operaciones masivas

Todas las operaciones que afectan a múltiples equipos se gestionan desde
**Acciones Masivas** en el admin de Django.

### Acceder

`Admin → Developments → Acciones Masivas → Añadir`

### Tipos de acción disponibles

| Acción                             | Descripción                                                               | Campos requeridos                            |
| ---------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------- |
| **Generate Initial Setup Presets** | Crea el snapshot v1 para cada equipo con un preset de personalidad        | `season`; `bias` (opcional, random si vacío) |
| **Apply Sponsor Affinity Bonuses** | Aplica +1 nivel en el departamento que potencia el patrocinador principal | `season`                                     |
| **Generate Circuit Setups**        | Genera (o regenera) el `.ini` de fin de semana para un circuito           | `season`, `circuit`                          |

### Filtros disponibles

- **Por temporada** — siempre requerido.
- **Por equipo** — dejar en blanco para aplicar a todos los equipos de esa temporada.
- **Estado** — Pending / Completed OK / Completed with Errors.

### Log de resultados

Cada registro guarda el resultado línea a línea en el campo **Result Log**:

```
OK   Ferrari – 2026: preset 'speed' created (v1).
OK   Mercedes – 2026: preset 'cornering' created (v1).
SKIP Red Bull – 2026: A setup snapshot already exists for...
ERR  Alpine – 2026: No TeamDevelopment found...
```

### Re-ejecutar una acción

Selecciona uno o varios registros en la lista → `Action: Re-run selected actions`.

---

## Flujo completo de una temporada

### 1. Preparación inicial

```
Admin → Seasons → Crear temporada
Admin → Teams → Crear equipos y asignar patrocinadores (con condición type=affinity)
Admin → Developments → Team Developments → Crear un registro por equipo×temporada
```

O desde shell:

```python
from apps.developments.models import TeamDevelopment
from apps.seasons.models import Season
from apps.teams.models import Team

season = Season.objects.get(name="2026")
for team in Team.objects.all():
    TeamDevelopment.objects.get_or_create(team=team, season=season)
```

### 2. Aplicar bonificaciones de patrocinador

```
Acciones Masivas → Añadir
  Acción: Apply Sponsor Affinity Bonuses
  Season: 2026
  Team: (vacío = todos)
→ Guardar
```

O por comando:

```bash
python manage.py apply_season_bonuses 1
python manage.py apply_season_bonuses 1 --dry-run   # solo muestra, no guarda
```

### 3. Generar presets iniciales

```
Acciones Masivas → Añadir
  Acción: Generate Initial Setup Presets
  Season: 2026
  Team: (vacío = todos)
  Bias: (vacío = random, o p.ej. "speed")
→ Guardar
```

O por comando:

```bash
python manage.py init_season_setups 1
python manage.py init_season_setups 1 --bias speed
python manage.py init_season_setups 1 --dry-run
```

### 4. Configurar BOP (Balance of Performance)

```
Admin → Developments → Balance of Performance → Añadir
  Team: Alpine
  Season: 2026
  Ballast: +10      (kg extra, handicap)
  Restrictor: 5     (% de reducción de potencia)
```

El BOP se aplica automáticamente al generar cualquier `CircuitSetup`.

### 5. Generar setups de circuito

```
Acciones Masivas → Añadir
  Acción: Generate Circuit Setups
  Season: 2026
  Circuit: Monza
  Team: (vacío = todos)
→ Guardar
```

O manualmente por equipo:

```
Admin → Developments → Circuit Setups → Añadir
  Team / Season / Circuit → Guardar
```

Al guardar, el `.ini` se regenera automáticamente con el BOP incluido.

### 6. Aplicar una mejora

```
Admin → Developments → Purchased Upgrades → Añadir
  Team: Ferrari
  Season: 2026
  Department: engine
  Previous level: 1 → New level: 2
  Cost: 500000
  Applied: ✓
→ Guardar
```

Al marcar `applied=True`, el sistema:

1. Actualiza `TeamDevelopment.engine = 2`.
2. Genera `CarSetupSnapshot` v2 con solo los parámetros que cambiaron.
3. Muestra qué parámetros INI cambiaron en el mensaje flash.

> **Nota:** los niveles deben subir de 1 en 1 (1→2, 2→3…). Saltar niveles
> mostrará un error y no se guardará.

---

## Departamentos y sinergias

| Departamento   | Parámetros INI que controla                                          |
| -------------- | -------------------------------------------------------------------- |
| `engine`       | TURBO_BOOST_THRESHOLD, ENGINE_LIMITER                                |
| `aerodynamics` | FRONT_WING, REAR_WING                                                |
| `chassis`      | SPRING*RATE_LF/RF/LR/RR *(permanente)*, ROD_LENGTH*\* _(permanente)_ |
| `suspension`   | BUMP/REBOUND (rápido y lento), ANTI_ROLL                             |
| `electronics`  | DTC, ABS, ENGINE_BRAKE, COAST_MAP, PIT_LIMITER                       |

### Sinergias activas

| Combinación                  | Bonus                               |
| ---------------------------- | ----------------------------------- |
| engine ≥ 4 + chassis ≥ 3     | +5% en parámetros de motor y chasis |
| aero ≥ 4 + suspension ≥ 3    | +5% en aero y suspensión            |
| engine ≥ 3 + electronics ≥ 3 | +5% en electrónica                  |
| chassis ≥ 4 + suspension ≥ 4 | +8% en chasis y suspensión          |

---

## Personalidades de setup (Preset Bias)

| Bias          | Departamentos favorecidos |
| ------------- | ------------------------- |
| `speed`       | engine, aerodynamics      |
| `cornering`   | suspension, aerodynamics  |
| `consistency` | electronics, chassis      |
| `technical`   | electronics, suspension   |
| `raw_power`   | engine, chassis           |
| `balanced`    | todos por igual           |

El bias se asigna en la creación del snapshot v1 y se mantiene en todas las
versiones posteriores.

---

## Parámetros tunables vs permanentes

| Tipo            | Parámetros                                   | Editable por el piloto         |
| --------------- | -------------------------------------------- | ------------------------------ |
| **Permanentes** | `SPRING_RATE_*`, `ROD_LENGTH_*`              | ✗ — solo mejoras de chasis     |
| **Tunables**    | Alas, amortiguadores, diff, electrónica…     | ✓ — dentro del rango del nivel |
| **Fijos**       | Marchas, combustible, neumáticos, presiones… | Nunca se tocan                 |

Para ver los rangos disponibles de un equipo:

```python
from apps.developments.models import TeamDevelopment
from apps.developments import setup_generator as sg

dev = TeamDevelopment.objects.get(team__name="Ferrari", season__name="2026")
bounds = sg.get_tunable_bounds(dev, preset_bias="speed")
# {'FRONT_WING': (3, 7), 'REAR_WING': (4, 8), ...}
```

---

## Snapshots y versiones

- **v1** — creado por `generate_initial_preset` / `AccionMasiva`.
- **v2+** — creado automáticamente al aplicar una mejora que cambia al menos un parámetro.
- Si una mejora no cruza ningún umbral de sinergia ni cambia parámetros, **no se crea snapshot** (se muestra aviso).
- Los snapshots son de solo lectura en el admin — no se pueden crear manualmente.

Ver historial de un equipo:

```python
from apps.developments.setup_service import get_snapshot_history
history = get_snapshot_history(team, season)
for snap in history:
    print(snap.version, snap.changed_params)
```

---

## Puntuación de rendimiento

```python
from apps.developments import setup_generator as sg
score = sg.get_performance_rating(dev, circuit_key="monza")
# → float 0–100
```

Útil para calcular resultados de carrera. Se puede pasar junto con otros
factores (lluvia, degradación, etc.) en el simulador de carreras.

---

## Comandos de gestión disponibles

```bash
# Aplicar bonificaciones de patrocinador
python manage.py apply_season_bonuses <season_id> [--dry-run]

# Generar presets iniciales para todos los equipos de una temporada
python manage.py init_season_setups <season_id> [--bias <nombre>] [--dry-run]
```

---

## Errores frecuentes

| Error                                                | Causa                                                | Solución                                               |
| ---------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------ |
| "No TeamDevelopment records found"                   | No existe fila TeamDevelopment para esa season/team  | `Admin → Team Developments → Añadir`                   |
| "A setup snapshot already exists"                    | Ya se generó el preset v1                            | Normal — usar Re-run o saltar este equipo              |
| "Invalid upgrade: levels must increase by exactly 1" | Se intentó saltar un nivel                           | Ajustar `new_level = previous_level + 1`               |
| "No TeamDevelopment found for X in Y"                | Se aplicó un upgrade sin crear TeamDevelopment antes | Crear la fila TeamDevelopment primero                  |
| "A circuit must be selected"                         | Se lanzó Generate Circuit Setups sin elegir circuito | Seleccionar el campo Circuit en AccionMasiva           |
| "INI generation failed"                              | Template `.ini` no encontrado o parámetro inválido   | Verificar `templates/rss_formula_rss_3_v6_default.ini` |
