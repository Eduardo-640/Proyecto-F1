# Sim Racing Team Manager

## Sistema de Liga con Desarrollo Técnico para Assetto Corsa

## Descripción General

Sim Racing Team Manager es un sistema de gestión de campeonato diseñado para añadir una capa persistente de **gestión técnica, desarrollo del coche y economía** a una liga tradicional de simracing.

En lugar de competir únicamente con habilidad de conducción, cada participante gestiona un **equipo ficticio** que desarrolla su coche durante la temporada. El rendimiento final depende de múltiples factores combinados.

El sistema está pensado principalmente para **grupos pequeños (5 a 8 pilotos)** donde la coordinación es sencilla y donde añadir profundidad estratégica mejora la experiencia.

El proyecto introduce:

* Sistema económico persistente
* Desarrollo técnico del coche
* Eventos de carrera estructurados
* Balance competitivo dinámico
* Estrategia tanto dentro como fuera de pista

El objetivo es que cada carrera tenga consecuencias y que la temporada genere una progresión narrativa natural entre equipos.

---

# Concepto del Campeonato

Cada piloto representa un **equipo de competición ficticio**.

Todos los equipos comienzan con un coche poco desarrollado y deben mejorar su rendimiento mediante:

* resultados en carrera
* inversión en desarrollo
* decisiones estratégicas

El rendimiento final del coche se define mediante la combinación:

```
Rendimiento = Habilidad del piloto + Desarrollo del coche + Setup + Estrategia
```

Esto permite que pilotos con menor nivel puedan mantenerse competitivos mediante el desarrollo del coche, mientras que pilotos muy rápidos deben gestionar también el progreso técnico.

---

# Escala del Campeonato

Configuración recomendada para la primera temporada:

| Parámetro          | Valor                     |
| ------------------ | ------------------------- |
| Pilotos            | 5                         |
| Carreras           | 7                         |
| Circuitos          | 7                         |
| Duración carrera   | 40–50 minutos             |
| Duración temporada | aproximadamente 7 semanas |

El sistema puede ampliarse hasta aproximadamente **8–10 pilotos** sin cambios estructurales importantes.

---

# Estructura del Fin de Semana de Carrera

Cada ronda del campeonato se desarrolla a lo largo de aproximadamente **4 o 5 días**.

## Periodo de Práctica

Duración recomendada: **2 a 3 días**

Durante este periodo el servidor permanece abierto y los pilotos pueden entrenar libremente.

Opcionalmente se puede aplicar un sistema de equilibrio donde los pilotos peor clasificados disponen de más tiempo de entrenamiento.

| Posición en campeonato | Días de práctica |
| ---------------------- | ---------------- |
| 1º                     | 1 día            |
| 2º–3º                  | 2 días           |
| 4º–5º                  | 3 días           |

Este sistema ayuda a que pilotos con menor rendimiento puedan prepararse mejor.

---

## Clasificación

Duración recomendada:

20 minutos

Formato:

* sesión abierta
* vueltas lanzadas
* sin reinicios de sesión

La pole position puede recibir una pequeña bonificación económica o de puntos.

---

## Carrera

Duración recomendada:

40 a 50 minutos

Esta duración permite introducir:

* degradación de neumáticos
* estrategias de combustible
* paradas en boxes

---

# Configuración Recomendada de Carrera

| Parámetro              | Valor recomendado |
| ---------------------- | ----------------- |
| Desgaste de neumáticos | 150%              |
| Consumo de combustible | 100%              |

Se recomienda incluir:

**1 parada obligatoria en boxes**

Esto introduce decisiones estratégicas reales.

---

# Sistema Económico

Cada equipo dispone de una cantidad de **créditos** que representan recursos del equipo.

Los créditos se utilizan para comprar mejoras del coche.

Los créditos se obtienen principalmente mediante resultados en carrera.

## Recompensas de Carrera

| Posición | Créditos |
| -------- | -------- |
| 1        | 200      |
| 2        | 170      |
| 3        | 150      |
| 4        | 120      |
| 5        | 100      |

Bonificaciones adicionales:

| Logro            | Recompensa |
| ---------------- | ---------- |
| Pole position    | +40        |
| Vuelta rápida    | +30        |
| Terminar carrera | +20        |

Los créditos se almacenan de forma persistente entre carreras.

---

# Sistema de Desarrollo del Coche

El coche se divide en varios **departamentos técnicos**.

| Departamento | Función                |
| ------------ | ---------------------- |
| Motor        | Velocidad punta        |
| Aerodinámica | Rendimiento en curva   |
| Chasis       | Estabilidad general    |
| Suspensión   | Desgaste de neumáticos |
| Electrónica  | Tracción               |

Cada departamento tiene niveles del **1 al 5**.

Configuración inicial del coche:

```
Motor = 1
Aerodinámica = 1
Chasis = 1
Suspensión = 1
Electrónica = 1
```

---

# Coste de Mejoras

Las mejoras tienen un coste progresivo para evitar progresión excesivamente rápida.

| Mejora      | Coste |
| ----------- | ----- |
| Nivel 1 → 2 | 150   |
| Nivel 2 → 3 | 300   |
| Nivel 3 → 4 | 600   |
| Nivel 4 → 5 | 1000  |

Esto obliga a planificar el desarrollo.

---

# Implementación Técnica

Las mejoras se aplican mediante parámetros del servidor utilizando archivos `.ini`.

Los principales mecanismos de control son:

* restrictor de potencia
* ballast (lastre)
* presets de setup

Estos parámetros se configuran en el archivo:

```
entry_list.ini
```

Ejemplo:

```
[CAR_0]
MODEL=rss_formula_rss_3
GUID=7656119XXXXXXXX
BALLAST=30
RESTRICTOR=4
```

---

# Balance Inicial del Coche

Todos los coches comienzan con penalizaciones para simular coches poco desarrollados.

Configuración base:

```
BALLAST = 40
RESTRICTOR = 5
```

Las mejoras eliminan progresivamente estas penalizaciones.

---

# Efectos de las Mejoras

## Motor

Reduce el restrictor.

| Nivel | Restrictor |
| ----- | ---------- |
| 1     | 5          |
| 2     | 4          |
| 3     | 3          |
| 4     | 2          |
| 5     | 0          |

Efecto: aumento de velocidad punta.

---

## Aerodinámica

Reduce el ballast.

| Nivel | Ballast |
| ----- | ------- |
| 1     | 40 kg   |
| 2     | 30 kg   |
| 3     | 20 kg   |
| 4     | 10 kg   |
| 5     | 0 kg    |

Efecto: mejora de paso por curva.

---

## Chasis

Ajusta estabilidad del coche mediante presets de setup.

Ejemplo:

```
[ARB]
FRONT=3
REAR=2
```

Efecto:

* mejor estabilidad
* mejor comportamiento en entrada de curva

---

## Suspensión

Ajusta parámetros como:

```
SPRING_RATE
CAMBER
TOE
```

Efecto:

* menor degradación de neumáticos
* mayor consistencia en stints largos

---

## Electrónica

Ajusta parámetros de diferencial y control de tracción.

```
DIFFERENTIAL_PRELOAD
TRACTION_CONTROL
```

Efecto:

* mejor salida de curva
* menos pérdidas de tracción

---

# Generación Automática de Setups

Un sistema backend puede generar automáticamente presets de setup para cada equipo.

Ejemplo de estructura de archivos:

```
/setups/
    team_alpha_monza.ini
    team_beta_monza.ini
```

Estos setups combinan:

* mejoras del equipo
* características del circuito
* configuración base del coche

---

# Aplicación de Mejoras

Las mejoras **no se aplican inmediatamente**.

Flujo recomendado:

1. Se disputa la carrera
2. Se calculan recompensas
3. Los equipos compran mejoras
4. Las mejoras se aplican antes del siguiente evento

Esto evita abusos durante el periodo de práctica.

---

# Sistema de Balance Competitivo

Se pueden aplicar sistemas adicionales para equilibrar la competición.

## Ventaja de entrenamiento

Pilotos peor clasificados reciben más tiempo de práctica.

## Bonificación económica

Pilotos retrasados reciben créditos adicionales.

Ejemplo:

| Posición | Bonus |
| -------- | ----- |
| 1        | 0     |
| 2        | +20   |
| 3        | +40   |
| 4        | +60   |
| 5        | +80   |

---

# Flujo Administrativo

El proceso de cada evento es el siguiente:

1. El servidor ejecuta sesiones de práctica
2. Se celebra clasificación
3. Se disputa la carrera
4. El servidor genera resultados
5. El sistema procesa resultados
6. Se asignan créditos
7. Los equipos compran mejoras
8. Se actualizan parámetros del servidor

---

# Escenarios Especiales

## Piloto ausente

El piloto mantiene sus mejoras pero no recibe créditos de carrera.

---

## Nuevo piloto en mitad de temporada

Se recomienda que comience con:

```
nivel medio de mejoras de la parrilla
```

Esto evita que quede demasiado atrás.

---

## Dominancia excesiva

Posibles soluciones:

* reducción de días de práctica
* ajustes económicos
* limitaciones de desarrollo

---

# Ventajas del Sistema

* Introduce estrategia fuera de pista
* Reduce diferencias extremas entre pilotos
* Añade narrativa a la temporada
* Mantiene interés constante

---

# Riesgos Potenciales

| Riesgo                 | Mitigación                    |
| ---------------------- | ----------------------------- |
| Mejoras desbalanceadas | sistema de costes progresivos |
| Dominancia de piloto   | balance económico             |
| Manipulación de setups | uso de presets oficiales      |

---

# Posibles Expansiones Futuras

El sistema puede ampliarse con:

* patrocinadores
* contratos de piloto
* ingenieros especializados
* desarrollo secreto
* mejoras específicas por circuito
* progresión entre temporadas

---

# Conclusión

Sim Racing Team Manager transforma una liga tradicional en un sistema competitivo persistente donde **habilidad de conducción, gestión técnica y estrategia económica** determinan el resultado final del campeonato.
