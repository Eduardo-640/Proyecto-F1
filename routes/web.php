<?php

use App\Http\Controllers\ProfileController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\CarrerasController;
use App\Http\Controllers\PilotosController;
use App\Http\Controllers\EquiposController;
use App\Http\Controllers\NoticiasController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\authSesion;
use App\Http\Controllers\PerfilController;

// Route::get('/welcome', function () {
//     return Inertia::render('Welcome', [
//         'canLogin' => Route::has('login'),
//         'canRegister' => Route::has('register'),
//         'laravelVersion' => Application::VERSION,
//         'phpVersion' => PHP_VERSION,
//     ]);
// });

// Route::get('/dashboard', function () {
//  return Inertia::render('Dashboard');
// })->middleware(['auth', 'verified'])->name('dashboard');

// Route::middleware('auth')->group(function () {
//     Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
//     Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
//     Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
// });

#########################
# Rutas de la pagina F1 #
#########################
Route::get('/', [HomeController::class, 'index']);  // Pagina de Inicio
Route::get('/api/proximaCarrera', [CarrerasController::class, 'proximaCarrera']);
Route::get('/api/calendarioCarreras', [CarrerasController::class, 'calendarioCarreras']);
Route::get('/api/calificacionesActuales', [PilotosController::class, 'calificacionesActuales']);

// Pagina de Pilotos
Route::get('/pilotos', [PilotosController::class, 'index']);
Route::get('/api/pilotos/{year}/detalles/{id}', [PilotosController::class, 'verPiloto']);
Route::get('/api/pilotos/{year}', [PilotosController::class, 'PilotosPorAnho']);

// Pagina de Equipos
Route::get('/equipos', [EquiposController::class, 'index']);
Route::get('/api/equipos/{year}', [EquiposController::class, 'obtenerEquipos']);


// Pagina de Carreras
Route::get('/carreras', [CarrerasController::class, 'index']);  
Route::get('/api/carreras/{year}', [CarrerasController::class, 'obtenerCarreras']);
Route::get('/api/carrera/{year}/{round}', [CarrerasController::class, 'verCarrera']);

// Pagina de Noticias
Route::get('/noticias', [NoticiasController::class, 'index']);
Route::get('/api/noticias', [NoticiasController::class, 'obtenerNoticias']);


// Rutas para el inicio de sesión personalizado
Route::get('/login', function () {
    return inertia('Auth/Login');
})->name('login');

Route::post('/login', [authSesion::class, 'login']);
Route::post('/logout', [authSesion::class, 'logout'])->name('logout');

Route::middleware(['auth'])->group(function () {
    Route::get('/perfil', [PerfilController::class, 'index'])->name('perfil');
});

require __DIR__.'/auth.php';
