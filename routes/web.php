<?php

use App\Http\Controllers\ProfileController;
use Illuminate\Foundation\Application;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\CarrerasController;

Route::get('/welcome', function () {
    return Inertia::render('Welcome', [
        'canLogin' => Route::has('login'),
        'canRegister' => Route::has('register'),
        'laravelVersion' => Application::VERSION,
        'phpVersion' => PHP_VERSION,
    ]);
});

Route::get('/dashboard', function () {
    return Inertia::render('Dashboard');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

#########################
# Rutas de la pagina F1 #
#########################
Route::get('/', [HomeController::class, 'index']);  // Pagina de Inicio

Route::get('/pilotos', function () {                // Pagina de Pilotos
    return Inertia::render('Pilotos');
});

Route::get('/equipos', function () {                // Pagina de Equipos
    return Inertia::render('Equipos');
});

Route::get('/carreras', [CarrerasController::class, 'index']);  // Pagina de Carreras

// Rutas de la API
Route::get('/api/carreras/{year}', [CarrerasController::class, 'obtenerCarreras']);
Route::get('/api/carrera/{year}/{round}', [CarrerasController::class, 'verCarrera']);

Route::get('/noticias', function () {                // Pagina de Noticias
    return Inertia::render('Noticias');
});

require __DIR__.'/auth.php';
