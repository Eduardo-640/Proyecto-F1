# Proyecto de Fórmula 1 - Plataforma Web Interactiva

Este proyecto es una plataforma web dedicada a los fans de la Fórmula 1, donde los usuarios pueden consultar noticias actualizadas, explorar información detallada sobre cada carrera de la temporada, y participar en una competición de F1 Fantasy League. La plataforma ofrece una experiencia completa e interactiva que combina datos de las carreras con una competición que fomenta la participación activa y la comunidad.

## Características

- **Noticias Actualizadas**: Los usuarios pueden consultar las últimas noticias sobre la Fórmula 1.
- **Detalles de Carreras**: Información detallada de cada carrera de la temporada, incluyendo resumen, mapa del circuito, clima y estadísticas.
- **F1 Fantasy League**: Los usuarios pueden elegir pilotos y escuderías para participar en una competición fantasy durante la temporada.
- **Interactividad y Visualización**: Estadísticas y datos visuales que mejoran la experiencia del usuario.
  
## Tecnologías Utilizadas

- **Frontend**: 
  - React
  - Lucide-React
  - Bootstrap
  - TailwindCSS
  
- **Backend**: 
  - PHP
  - Laravel 11
  - Laravel-Breeze (para autenticación)
  
- **Base de Datos**: MySQL
  
- **Herramientas y Dependencias**:
  - Composer (para gestión de dependencias PHP)
  - Node.js (para gestionar las dependencias de JavaScript)
  - Curl (para realizar peticiones HTTP a la API)

- **API**:
  - [Ergast API](http://api.jolpi.ca/ergast/) para obtener datos de la Fórmula 1 (como pilotos, escuderías, carreras, resultados y más).

## Instalación

### Requisitos Previos

1. **PHP** (preferiblemente versión 8.1 o superior)
2. **MySQL**
3. **Node.js** (preferiblemente versión 16 o superior)
4. **Composer** (para gestionar dependencias PHP)

### Pasos para la instalación

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/Eduardo-640/Proyecto-F1.git
   cd Proyecto-F1

2. **Instalar dependencias del backend**

    ```bash
    composer install

3. **Instalar dependencias del frontend**

    ```bash
    npm install

4. **Configuración del entorno**

    ```bash
    cp .env.example .env

5. **realiza las migraciones**

    ```bash
    php artisan migrate

6. **Compilar el frontend**

    ```bash
    npm run build

7. **Ejecutar el servidor de desarrollo**

    ```bash
    php artisan serve
