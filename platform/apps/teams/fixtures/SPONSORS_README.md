# Sponsors CSV — Guía de diseño y mecánicas

## 1. Formato del CSV

```
name;description;base_bonus;is_main;active;engine;aerodynamics;electronics;chassis;suspension;development;consistency;podiums;money;wins;points;speed
```

| Campo          | Tipo       | Descripción                                                      |
| -------------- | ---------- | ---------------------------------------------------------------- |
| `name`         | texto      | Nombre del sponsor                                               |
| `description`  | texto      | Descripción temática / narrativa                                 |
| `base_bonus`   | entero ≥ 0 | Créditos base del contrato (pool de pagos de la temporada)       |
| `is_main`      | true/false | Si es el sponsor principal del equipo (solo uno activo a la vez) |
| `active`       | true/false | Si el sponsor está disponible para contratarse                   |
| **Categorías** | -1 / 0 / 1 | Ver sección 2                                                    |
| `money`        | entero ≥ 1 | Valor económico (ver sección 4). **No es affinity ni penalty**   |

> El campo `money` siempre vale al menos `1`. Los campos de categoría no-money solo admiten `-1`, `0` o `+1`.

---

## 2. Categorías y su efecto en departamentos al inicio de temporada

Cuando un equipo firma un **sponsor principal** (`is_main=True`), sus condiciones se aplican como bonificación de nivel de departamento al inicio de la temporada (llamada `apply_starting_bonuses`).

### Mapa de categoría → departamento

| Categoría CSV  | Departamento afectado | Lógica                                      |
| -------------- | --------------------- | ------------------------------------------- |
| `engine`       | Engine                | Directo                                     |
| `aerodynamics` | Aerodynamics          | Directo                                     |
| `electronics`  | Electronics           | Directo                                     |
| `chassis`      | Chassis               | Directo                                     |
| `suspension`   | Suspension            | Directo                                     |
| `development`  | Chassis               | R&D estructural → rigidez del chasis        |
| `speed`        | Engine                | Velocidad punta → potencia del motor        |
| `wins`         | Engine                | Mentalidad ganadora → motor dominante       |
| `consistency`  | Suspension            | Gestión de neumáticos → suspensión adaptiva |
| `podiums`      | Aerodynamics          | Presencia en cabeza → velocidad en curva    |
| `points`       | _(ninguno)_           | Solo afecta pago por carrera                |

### Reglas de aplicación

- Afínity (`+1`) → el departamento correspondiente **sube 1 nivel** al inicio
- Penalty (`-1`) → el departamento correspondiente **baja 1 nivel** al inicio
- Los niveles están clampeados entre **1 y 5**
- Si dos categorías apuntan al mismo departamento (ej. `engine` + `speed`), el resultado se clampea a **±1** (no se acumula más)

---

## 3. Sinergias entre departamentos

Si el sponsor principal tiene **dos departamentos complementarios** ambos en `+1`, se genera un bonus extra en un tercer departamento sinérgico (también clampeado a +1). Lo mismo aplica en sentido negativo.

| Par afectado                  | Departamento sinérgico |
| ----------------------------- | ---------------------- |
| `engine` + `aerodynamics`     | Electronics            |
| `chassis` + `suspension`      | Aerodynamics           |
| `engine` + `electronics`      | Aerodynamics           |
| `aerodynamics` + `suspension` | Chassis                |

**Ejemplo:** Un sponsor con `engine=1` y `aerodynamics=1` también otorga `electronics=+1` al inicio de temporada, aunque no tenga esa condición en el CSV.

---

## 4. El campo `money` — Descuento en mejoras

El campo `money` no es una condición de tipo affinity/penalty. Representa la capacidad económica del sponsor para **reducir el costo de las mejoras** durante la temporada.

Cada unidad de `money` aplica un **5% de descuento** sobre el costo de las mejoras:

```
multiplicador = 1.0 - (0.05 × money_value)
costo_final   = costo_base × multiplicador
```

| money | Descuento | Multiplicador |
| ----- | --------- | ------------- |
| 1     | 5%        | 0.95          |
| 2     | 10%       | 0.90          |
| 3     | 15%       | 0.85          |

> El multiplicador está clampeado en el rango `[0.5, 2.0]`. Solo aplica al **sponsor principal** activo.

---

## 5. Multiplicador de pago por rendimiento en carrera

Cinco categorías del CSV modifican el pago que recibe el equipo por cada carrera, según el resultado obtenido. El sistema lo gestiona el comando `settle_sponsor_payouts`.

### Fórmula base de pago

```
pago = remaining_amount × RATE(0.25) × perf × sponsor_mult
```

Donde:

- `remaining_amount` → créditos pendientes del contrato
- `RATE` → fracción que se paga por carrera (25%)
- `perf` → puntos del equipo / puntos del mejor equipo de la carrera
- `sponsor_mult` → modificador por condiciones del sponsor (ver tabla)

### Condiciones de rendimiento

| Categoría     | Logro requerido                       | Bonus si se cumple |
| ------------- | ------------------------------------- | ------------------ |
| `wins`        | El equipo gana la carrera             | +30%               |
| `podiums`     | El equipo termina top-3               | +20%               |
| `consistency` | El equipo puntúa (cualquier posición) | +15%               |
| `speed`       | El equipo hace la vuelta rápida       | +15%               |
| `points`      | El equipo puntúa (cualquier posición) | +10%               |

### Reglas del modificador

| Condición CSV   | Resultado             | Efecto                                       |
| --------------- | --------------------- | -------------------------------------------- |
| `+1` (affinity) | Logro alcanzado ✅    | +bonus                                       |
| `+1` (affinity) | Logro NO alcanzado ❌ | -bonus×0.5 (penalización reducida)           |
| `-1` (penalty)  | Logro NO alcanzado ❌ | +bonus (penaliza al equipo que compite bien) |
| `-1` (penalty)  | Logro alcanzado ✅    | sin efecto                                   |

El `sponsor_mult` final se clampea a **[0.5, 2.0]**.

---

## 6. Equilibrio de condiciones (`total_score`)

Cada sponsor tiene un campo `total_score` que es la suma de todos sus valores no-money:

```
total_score = engine + aerodynamics + electronics + chassis + suspension
            + development + consistency + podiums + wins + points + speed
```

**Regla de diseño: `total_score` debe ser siempre 0.** Esto garantiza que por cada categoría beneficiada hay una penalizada equivalente, creando decisiones estratégicas reales.

El comando `balance_sponsors --fix` puede rebalancear automáticamente cualquier sponsor desbalanceado.

---

## 7. Reglas de diseño para nuevos sponsors

Al crear un nuevo sponsor en el CSV:

1. **Contar affinities y penalties**: deben ser iguales en cantidad (ej. 2 en `+1` y 2 en `-1`, el resto en `0`)
2. **Coherencia temática**: las categorías afectadas deben tener sentido narrativo con el nombre/descripción
3. **`money`**: a mayor `base_bonus`, mayor `money` (más créditos = más descuento en mejoras)
4. **Sponsors principales** (`is_main=True`): pueden tener 3-4 condiciones activas; sponsors secundarios típicamente 1-2
5. **No usar `wins` o `points` como affinity en muchos sponsors**: son los más poderosos en payout y generan mucha ventaja si se acumulan

### Referencia rápida de valores `money` sugeridos

| `base_bonus`  | `money` sugerido |
| ------------- | ---------------- |
| < 5.000       | 1                |
| 5.000 – 9.999 | 2                |
| ≥ 10.000      | 3                |

---

## 8. Ciclo de vida al inicio de temporada

```
1. Equipo firma sponsor principal (is_main=True)
        ↓
2. apply_starting_bonuses(dev)
   → lee condiciones affinity/penalty del sponsor principal
   → mapea categorías → departamentos (via AFFINITY_DEPARTMENT)
   → aplica ±1 de nivel por departamento (clamp [1..5])
   → evalúa sinergias entre pares de departamentos
   → guarda niveles ajustados en TeamDevelopment
        ↓
3. generate_initial_preset(dev)
   → genera CarSetupSnapshot v1 con los niveles ya ajustados
        ↓
4. Durante la temporada: settle_sponsor_payouts (por carrera)
   → calcula pago base × perf × sponsor_mult
   → sponsor_mult varía según condiciones de rendimiento del sponsor
        ↓
5. get_sponsor_money_multiplier(team)
   → aplica descuento en cada compra de mejora (PurchasedUpgrade)
```
