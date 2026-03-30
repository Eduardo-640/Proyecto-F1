# Sim Racing Team Manager

## Sistema de Liga con Desarrollo Técnico para Assetto Corsa

Sim Racing Team Manager es una plataforma web para gestionar campeonatos de simracing con una capa persistente de **gestión técnica, desarrollo del coche y economía**. Cada participante dirige un equipo ficticio que evoluciona a lo largo de la temporada, combinando habilidad de conducción con decisiones estratégicas fuera de pista.

Pensado para grupos pequeños (5–8 pilotos) que compiten en Assetto Corsa y quieren añadir profundidad a su liga.

## Características

- **Gestión de temporadas y carreras**: seguimiento de resultados de práctica, clasificación y carrera importados directamente desde JSONs exportados por Assetto Corsa.
- **Sistema económico**: los pilotos acumulan créditos según sus resultados (puntos × multiplicador) para invertir en mejoras.
- **Desarrollo técnico de equipos**: cada equipo mejora departamentos (aerodinámica, motor, chasis…) con niveles 1–5 que se traducen en parámetros reales de setup de Assetto Corsa (`.ini`).
- **Generación automática de setups**: a partir del nivel de desarrollo del equipo y el circuito se generan setups optimizados.
- **Balance of Performance (BoP)**: ajuste dinámico para mantener la competitividad entre equipos con distintos niveles de desarrollo.
- **Clasificaciones y estadísticas**: standings de pilotos y equipos, victorias, podios, vueltas rápidas y más.
- **API REST**: interfaz completa para integrarse con el frontend o herramientas externas.

## Tecnologías

- **Backend**: Django 5 · Django REST Framework · SimpleJWT · django-cors-headers
- **Base de datos**: PostgreSQL 16 (vía Docker)
- **Frontend**: React 18 · Vite · TailwindCSS · Bootstrap 5 · Recharts · React Router DOM
- **Autenticación**: JWT (access + refresh tokens)
- **Infraestructura**: Docker (contenedor de base de datos)

## Estructura del proyecto

```
platform/          # Backend Django
  apps/
    seasons/       # Temporadas
    races/         # Carreras, resultados y escaneo de JSONs
    teams/         # Equipos y créditos
    drivers/       # Pilotos y autenticación
    developments/  # Desarrollo técnico y generación de setups
  config/          # Configuración de Django (base/dev/prod)

resources/js/      # Frontend React (Vite)
media/output/      # JSONs de resultados procesados (Assetto Corsa)
Docker/            # docker-compose para PostgreSQL
```

## Instalación

### Requisitos previos

- Python 3.11+
- Node.js 18+
- Docker y Docker Compose

### Pasos

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/Eduardo-640/Proyecto-F1.git
   cd Proyecto-F1
   ```

2. **Levantar la base de datos**

   ```bash
   docker compose -f Docker/docker-compose.yml up -d db
   ```

3. **Configurar el entorno del backend**

   ```bash
   cd platform
   cp .env.example .env
   # Edita .env y ajusta DATABASE_URL y SECRET_KEY
   ```

4. **Instalar dependencias del backend y migrar**

   ```bash
   pip install -r ../requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Instalar dependencias del frontend**

   ```bash
   cd ..
   npm install
   ```

6. **Ejecutar en desarrollo**

   ```bash
   # Backend (desde platform/)
   python manage.py runserver

   # Frontend (desde la raíz)
   npm run dev
   ```

Para más detalles sobre la configuración de la base de datos consulta [Docker/LOCAL_SETUP.md](Docker/LOCAL_SETUP.md).

## Flujo de resultados

Los resultados de las sesiones se exportan desde Assetto Corsa como JSON y se colocan en `media/input/`. El comando de gestión los procesa y mueve a `media/output/`:

```bash
python manage.py process_input_folder
```

Consulta [REWARDS.md](REWARDS.md) para ver cómo se calculan puntos y créditos por tipo de sesión.

---

## Enlaces

[Boceto](https://drive.google.com/file/d/1RZuLG6UakVBmFR7eloQtEuYeyeKAOVuV/view?usp=sharing) · [Análisis](https://drive.google.com/file/d/1r6Q0LrjlT5QrNJKy45wH99NtXDJmZR9N/view?usp=sharing) · [Diseño](https://drive.google.com/file/d/1863NhQfqDKNmjj7nRcM07e7eAPFYSEwh/view?usp=sharing) · [Pruebas](https://drive.google.com/file/d/1ILFDL6xcspfFlvdfQVYXzSWuS8slZmpw/view?usp=sharing) · [Video](https://youtu.be/FU6vX9cAtr0)