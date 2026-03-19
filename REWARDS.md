**Resumen**

- **Propósito:** Documentar el sistema de recompensas que procesa los ficheros exportados (Assetto Corsa) y explica qué aporta cada tipo de fichero a pilotos, equipos y créditos.

**Flujo resumido**

- Los JSON se escanean con el comando `process_input_folder` y cada archivo se procesa por `process_results`.
- Archivo → `RaceResult` (crear/actualizar) → `DriverStanding` (delta) → `Team.credits` (delta) + `CreditTransaction` (registro).
- Código relevante: [platform/apps/races/management/commands/process_input_folder.py](platform/apps/races/management/commands/process_input_folder.py), [platform/apps/races/management/commands/process_results.py](platform/apps/races/management/commands/process_results.py)

**Qué hace cada fichero (resumen por tipo)**

- **PRACTICE**

    - Puntos: ninguno (no afectan `DriverStanding.total_points`).
    - Créditos: ninguno (no generan `CreditTransaction`).
    - Pilotos/Equipos: se crean `Driver` y `Team` si no existen; se crea/actualiza `RaceResult` con posiciones y mejor vuelta si aplica.
    - Uso: útil para poblar pilotos y comprobar tiempos, no para recompensas.

- **QUALIFY / QUALIFYING**

    - Puntos: reducidos (top‑3 reciben 3/2/1 puntos por defecto).
    - Créditos: se calculan como `puntos * CREDIT_MULTIPLIER`.
    - Pilotos/Equipos: crea/actualiza `RaceResult`; marca posiciones y puede ajustar `DriverStanding` y `Team.credits` según deltas.
    - Uso: reconocimiento pequeño por la sesión de clasificación.

- **RACE**
    - Puntos: tabla completa (TOP‑10 por defecto: 25,18,15,12,10,8,6,4,2,1).
    - Créditos: `credits = puntos_delta * CREDIT_MULTIPLIER` (donde `puntos_delta` es la diferencia respecto al `RaceResult` previo, para idempotencia).
    - Pilotos/Equipos: actualiza `RaceResult` (posición, pole, fastest lap, finished), modifica `DriverStanding` (puntos, wins, podiums, races_entered, dnf_count, etc.) y registra `CreditTransaction` por cada ajuste.
    - Uso: otorga la mayor parte de puntos y créditos.

**Idempotencia y auditoría**

- El procesador calcula deltas comparando con un `RaceResult` existente para evitar duplicar puntos/creditos si un JSON se reprocesa.
- Cada movimiento de crédito crea una `CreditTransaction` (auditoría). Ver: [platform/apps/races/models.py](platform/apps/races/models.py)

**Constantes y configuración**

- `POINTS_TABLE` (race), `QUALIFY_POINTS` (qualify) y `CREDIT_MULTIPLIER` están en `process_results.py` y son la fuente de verdad para la asignación de puntos/créditos.
- Para cambiar reglas: editar `platform/apps/races/management/commands/process_results.py`.

**Casos prácticos y notas operativas**

- Si un JSON contiene pilotos nuevos: se crea `Driver` y se asigna/crea `Team` llamado `"<Driver> - Team"` salvo que el nombre sea vacío (usa `Unassigned`).
- Cuando se borra una `Race` (por admin o proceso), es recomendable usar las señales/herramientas de reversión si existen para deshacer `DriverStanding` y créditos asociados.
- Para forzar reprocesado seguro: actualizar/validar `RaceResult` existente o ejecutar comandos auxiliares que reviertan transacciones antes de re-aplicar.

**Cómo ejecutar (rápido)**

- Escanear carpeta `media/input` y mover a `media/output` tras procesar:

```bash
python manage.py process_input_folder
```

- Procesar un fichero concreto contra una `Race` conocida:

```bash
python manage.py process_results path/to/results.json --race-id <ID>
```

**Enlaces al código**

- Procesado de ficheros: [platform/apps/races/management/commands/process_input_folder.py](platform/apps/races/management/commands/process_input_folder.py)
- Lógica de puntos/créditos/idempotencia: [platform/apps/races/management/commands/process_results.py](platform/apps/races/management/commands/process_results.py)
- Modelos relacionados: [platform/apps/races/models.py](platform/apps/races/models.py)

Si quieres, puedo añadir ejemplos concretos con las tres JSON de `media/input` y mostrar exactamente los `CreditTransaction` que generan.

---

## Tablas rápidas

### Puntos por sesión

|   Sesión | Posición | Puntos |
| -------: | :------: | -----: |
|     Race |    1     |     25 |
|     Race |    2     |     18 |
|     Race |    3     |     15 |
|     Race |    4     |     12 |
|     Race |    5     |     10 |
|     Race |    6     |      8 |
|     Race |    7     |      6 |
|     Race |    8     |      4 |
|     Race |    9     |      2 |
|     Race |    10    |      1 |
|  Qualify |    1     |      3 |
|  Qualify |    2     |      2 |
|  Qualify |    3     |      1 |
| Practice |    -     |      0 |

> Nota: estos valores vienen de `POINTS_TABLE` y `QUALIFY_POINTS` en `process_results.py`.

### Créditos (ejemplo con `CREDIT_MULTIPLIER = 10`)

| Puntos adjudicados | Créditos generados |
| -----------------: | -----------------: |
|                 25 |                250 |
|                 18 |                180 |
|     3 (qualify 1º) |                 30 |
|                  0 |                  0 |

> Fórmula: `credit_delta = points_delta * CREDIT_MULTIPLIER`.

## ¿Qué significa "Race rewards delta for position 1"?

Cuando el sistema procesa un `RaceResult` crea (o actualiza) la fila y a continuación calcula la diferencia entre los puntos nuevos y los puntos que ya estaban registrados para ese `RaceResult` previo. Esa diferencia se llama `points_delta` y es la que determina cuántos créditos se añaden o quitan al `Team`.

Ejemplos:

- Escenario A — primer procesamiento:

    - No existe `RaceResult` previo para ese piloto en esa `Race`.
    - `position = 1` → `points_awarded = 25`.
    - `old_points = 0` (por ausencia) → `points_delta = 25 - 0 = 25`.
    - `credit_delta = 25 * 10 = 250` → se crea `CreditTransaction` con `amount = +250` y se suman 250 créditos al `Team`.

- Escenario B — corrección posterior (se procesó mal y ahora se corrige):
    - Existía `RaceResult` con `points_awarded = 25` y `Team` ya recibió +250.
    - Nuevo procesamiento corrige la posición a `position = 4` → `points_awarded = 12`.
    - `points_delta = 12 - 25 = -13`.
    - `credit_delta = -13 * 10 = -130` → se crea `CreditTransaction` con `amount = -130` y se restan 130 créditos al `Team`.

En la interfaz administrativa verás esas transacciones listadas con la descripción `Race rewards delta for position X` — ahí X es la posición actual que se guarda en `RaceResult`.

## Consejos operativos

- Antes de reprocesar un JSON que creas que ya fue aplicado, comprueba `RaceResult` y `CreditTransaction` para entender qué deltas se producirán.
- Si vas a forzar una corrección masiva, considera revertir las `CreditTransaction` asociadas (o usar comandos de mantenimiento) antes de reprocesar, para evitar movimientos inesperados.
