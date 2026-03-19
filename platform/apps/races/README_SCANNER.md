Resumen rápido del escaneo y actualización de carreras

Objetivo

- Escanear JSONs en `media/input`, procesarlos y moverlos a `media/output`.
- Asociar resultados a una `Race` existente o crear una nueva cuando sea necesario.

Cómo el escáner infiere la `Season` y `Round`

1. Preferible: nombre del fichero forzando temporada/round

    - Formato: `YYYY_<round>_<type>.json` (ej. `2026_2_race.json`)
    - Tipos: `practice`, `qualify` (o `qualifying`), `race`
    - Si existe, el escáner usará `season=YYYY` y `round=<round>`.

2. Fecha/hora en el nombre (inferir por fecha)

    - Formato: `YYYY_MM_DD_HH_MM_<type>.json` (ej. `2026_03_15_23_42_race.json`)
    - El escáner tomará la fecha y buscará la `Season` que cubra esa fecha
      (`Season.start_date <= date <= Season.end_date`).
    - Estricto: si la fecha NO está cubierta por exactamente UNA `Season`, el
      fichero se ignorará para evitar asignaciones incorrectas. En ese caso
      verás una advertencia y deberás renombrar el fichero o usar `--race-id`.

3. Dentro del JSON
    - El escáner usa `TrackName` para emparejar `Circuit` y `Type`/`Session`
      para decidir `status` (race/qualifying/practice).
    - Actualmente NO lee `season` o `round` desde campos internos del JSON.

Protección contra temporadas solapadas (comportamiento nuevo)

- Si varias `Season` cubren la misma fecha (solapamiento), el escáner
  considerará la situación AMBIGUA y NO seleccionará una `Season` automáticamente.
- En ese caso el fichero se saltará y se mostrará una advertencia pidiendo:
    - renombrar el fichero con `YYYY_round_type.json`, o
    - ejecutar `process_results` con `--season`/`--round` o `--race-id`.

Idempotencia y duplicados

- Si el escáner asocia el JSON con una `Race` existente, `process_results`
  actualiza `RaceResult` y aplica deltas (no duplica puntos/creditos si
  no hay cambios). Se registran transacciones de puntos (`DriverPointTransaction`)
  y de créditos (`CreditTransaction`) cuando hay deltas.
- Los ficheros procesados se mueven a `media/output` para evitar reprocesos.

Recomendaciones prácticas

- Para subir una carrera sin ambigüedades usa `YYYY_round_type.json`.
- Para forzar asociación a una `Race` concreta usa:
  `python manage.py process_results --race-id <id> <file>`
- Si prefieres que el escáner lea `season`/`round` desde el JSON, puede
  implementarse; solicítalo si lo deseas.

Archivos relevantes

- `platform/apps/races/management/commands/process_input_folder.py`
- `platform/apps/races/management/commands/process_results.py`
