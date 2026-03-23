# Guía de Migración del Backend a Postgres (Docker)
## 1. Preparar el contenedor
1. Asegúrate de tener Docker Desktop instalado y funcionando en WSL.
2. Desde la raíz del repo levanta la base:
   ```bash
   docker compose -f Docker/docker-compose.yml up -d db
   ```
   - Servicio: `f1_postgres`
   - Imagen: `postgres:16-alpine`
   - Credenciales: `simracing` / `simracing`
   - Puerto expuesto: `localhost:5432`
   - Datos persistidos en el volumen `postgres_data`

## 2. Configurar Django
   1. Entra al backend:
      ```bash
      cd platform
      ```
   2. Copia la plantilla de entorno si aún no existe:
      ```bash
      cp .env.example .env
      ```
   3. Edita platform/.env y agrega/ajusta:
      `DATABASE_URL=postgresql://simracing:simracing@localhost:5432/simracing`
   4. Instala dependencias (incluye psycopg2-binary):
      ```bash
      pip install -r ../requirements.txt
      ```
## 3. Ejecutar migraciones
   1. Aplica el esquema sobre Postgres:
      ```bash
      python manage.py migrate
      ```
   2. Comprueba las tablas creadas:
      ```bash
      docker exec -it f1_postgres psql -U simracing -d simracing -c '\dt'
      ```
## 4. Migrar datos existentes (opcional)
   1. Antes de cambiar a Postgres, con la base actual (por ejemplo SQLite) activa, genera un respaldo:
      ```bash
      python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup.json
      ```
   2. Cambia DATABASE_URL a Postgres (como en el paso 2) y carga los datos:
      ```bash
      python manage.py loaddata backup.json
      ```
      ```bash
      rm backup.json
      ```
## 5. Consejos útiles
- Reiniciar la base desde cero (¡elimina datos!):
   ```bash
    docker compose -f Docker/docker-compose.yml down -v
    docker compose -f Docker/docker-compose.yml up -d db
   ```
- Usa psql dentro de WSL (`sudo apt install postgresql-client`) para depuración rápida.
- El backend utiliza `dj_database_url` en `config/settings/development.py`, por lo que basta con ajustar DATABASE_URL.