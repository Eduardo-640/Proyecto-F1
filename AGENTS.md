# AGENTS.md - Proyecto Formula 1

Este es un proyecto **Laravel 11 + React (Inertia.js)** para una aplicacion de Formula 1 con una funcionalidad de Fantasy Manager.

---

## Comandos de Build

### Frontend (Node.js)

```bash
# Servidor de desarrollo (ejecuta Vite + Laravel dev)
npm run dev

# Build de produccion
npm run build

# Lint con auto-correccion
npm run lint
```

### Backend (PHP/Laravel)

```bash
# Instalar dependencias
composer install

# Ejecutar servidor de desarrollo con cola y logs
composer run dev

# Iniciar solo el servidor Laravel
php artisan serve

# Limpiar caches
php artisan optimize:clear
```

---

## Comandos de Testing

### Tests PHP (Pest/Laravel)

```bash
# Ejecutar todos los tests
php artisan test

# Ejecutar un archivo de test especifico
php artisan test tests/Feature/HomeControllerTest.php

# Ejecutar un metodo de test especifico
php artisan test --filter=test_index

# Ejecutar tests con cobertura
php artisan test --coverage

# Ejecutar suite de tests especifica
php artisan test --testsuite=Feature
php artisan test --testsuite=Unit
```

### Patron para Archivo de Test Individual

```bash
# Usando Pest directamente
./vendor/bin/pest tests/Feature/HomeControllerTest.php

# Un solo metodo de test
./vendor/bin/pest tests/Feature/HomeControllerTest.php --filter=test_index
```

---

## Guias de Estilo de Codigo

### PHP (Laravel)

- **Estandar**: PSR-12 con convenciones de Laravel
- **Formateador**: Laravel Pint (ejecutar `composer pint` para auto-correccion)
- **Namespace**: Usar `App\Http\Controllers`, `App\Models`, etc.
- **Nombrado de controladores**: `PascalCaseController.php` (ej. `HomeController.php`)
- **Nombrado de modelos**: `PascalCase.php` singular (ej. `Piloto.php`)
- **Metodos**: camelCase (ej. `getPilotos`, `comprarPiloto`)
- **Tablas de BD**: snake_case plural (ej. `usuarios`, `pilotos`)
- **Imports**: Agrupar por framework, paquetes, luego codigo de aplicacion
- **DocBlocks**: Usar anotaciones `@param`, `@return` para type hints
- **Validacion**: Usar `$request->validate([...])` en controladores
- **Respuestas de error**: Devolver `response()->json([...], codigoEstado)`

### React/JavaScript (JSX)

- **Estandar**: ES6+, React 18 con Hooks
- **Formateador**: Prettier (prettier-plugin-tailwindcss, prettier-plugin-organize-imports)
- **Comillas**: Simples (`'...'`)
- **Indentacion**: 4 espacios
- **Archivos de componentes**: PascalCase (ej. `Home.jsx`, `Navbar.jsx`)
- **Nombres de componentes**: PascalCase, igual al nombre del archivo
- **Estructura de componentes**:
  1. Imports (externos, luego internos)
  2. Funcion del componente
  3. Export default
- **Props**: Destructurar en la firma de la funcion
- **Estado**: Usar `useState`, `useEffect`
- **Refs**: `useRef` para acceso DOM, `useImperativeHandle` para forwardRef
- **Manejadores de eventos**: Patron `handleXxx`
- **Clases**: Clases de Tailwind CSS (kebab-case)

### Convenciones de Estructura de Archivos

```
resources/js/
├── app.jsx                    # Punto de entrada de la app
├── Pages/                     # Componentes de pagina (Inertia)
│   ├── Home.jsx
│   ├── Auth/
│   │   └── Login.jsx
│   └── Fantasy/
│       └── Equipos.jsx
├── Components/
│   ├── default/               # Componentes UI reutilizables
│   │   ├── TextInput.jsx
│   │   └── Button.jsx
│   ├── cabeceras/             # Componentes de cabecera
│   │   └── Navbar.jsx
│   └── ui/                    # UI especializada
│       └── BanderaPaises.jsx
└── Layouts/                   # Layouts de pagina
    └── MainLayout.jsx

app/Http/Controllers/
├── Controller.php
├── HomeController.php
├── Auth/
│   └── AuthenticatedSessionController.php
└── FantasyController.php

app/Models/
├── User.php
├── Piloto.php
└── Equipo.php
```

### Convenciones de Imports

**Componentes React**:
```jsx
// Paquetes externos
import React from 'react';
import { useState, useEffect } from 'react';

// Inertia
import { Link, usePage } from '@inertiajs/react';

// Componentes internos con alias @
import Navbar from '@/Components/cabeceras/Navbar';
import TextInput from '@/Components/default/TextInput';

// Imports relativos
import './globals.css';
```

**PHP**:
```php
<?php

namespace App\Http\Controllers;

use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Http\Request;
use App\Models\Piloto;
use Illuminate\Support\Facades\Auth;
```

### Uso de Tailwind CSS

- Usar alias `@` para resolucion de rutas en JSX
- Clases de Tailwind para todo el estilo (sin estilos inline)
- Tema oscuro base: `bg-black text-white`
- Color de acento: `red-600` (marca F1)
- Usar clase personalizada `font_enlaces` para enlaces de navegacion
- Prefijos responsivos: `sm:`, `md:`, `lg:`, `xl:`

### Manejo de Errores

**React**:
- Usar componente `InputError` para mostrar validacion de formularios
- Manejar errores de API en bloques try/catch
- Mostrar errores via prop `errors` de Inertia

**Laravel**:
- Devolver respuestas JSON con codigos de estado para rutas API
- Usar `$request->validate()` para validacion de entrada
- Registrar errores con `\Log::error()` o `\Log::warning()`
- Usar `findOrFail()` para busquedas de modelo con fallback 404

### Convenciones de Base de Datos

- Usar modelos Eloquent con propiedad `$table` para nombres no estandar
- Metodos de relacion: `belongsTo`, `belongsToMany`, `hasMany`
- Tablas pivote: `snake_case` con orden alfabetico (ej. `usuario_piloto`)
- Asignacion masiva: Definir array `$fillable`

---

## Notas Especificas del Proyecto

- **Autenticacion**: Laravel Sanctum + Inertia auth
- **Permisos**: Spatie Laravel Permission
- **Base de datos**: SQLite (platform/db.sqlite3)
- **Caracteristica Fantasy**: Usuarios pueden comprar/vender pilotos, gestionar presupuesto
- **Integracion API**: Datos F1 externos de `api.jolpi.ca/ergast`
- **Rutas de imagenes**: Usar `/images/` o `/favicon-32x32.png`

---

## TypeScript/PropTypes

Actualmente usando:
- JavaScript con patrones JSDoc
- React PropTypes deshabilitado en configuracion ESLint
- Sin TypeScript (eleccion legacy)

---

## Tareas Comunes

### Crear una nueva pagina:
1. Crear componente en `resources/js/Pages/`
2. Crear metodo de controlador devolviendo `Inertia::render('PageName')`
3. Agregar ruta en archivo de rutas de Laravel
4. Crear enlace en menu si es necesario

### Crear un componente reutilizable:
1. Crear en `resources/js/Components/`
2. Usar `forwardRef` para componentes que necesiten refs
3. Exportar por defecto
4. Importar usando alias `@/`

### Agregar un modelo de base de datos:
1. Crear modelo en `app/Models/`
2. Definir `$table`, `$fillable`, `$hidden`, `$casts`
3. Definir relaciones
4. Crear migracion si es necesario
