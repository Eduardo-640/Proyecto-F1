<?php

namespace App\Http\Controllers;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class EquiposController extends Controller
{
    //
    public function index(): Response
    {
        return Inertia::render('Equipos');
    }

    public function obtenerEquipos($year)
    {
        $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}/constructors.json");
        
        // Si la solicitud es exitosa, extrae los datos de los equipos
        if ($response->successful()) {
            $data = $response->json();
            $equipos = $data['MRData']['ConstructorTable']['Constructors'] ?? [];
        } else {
            // Si la solicitud falla, devuelve un error 404
            return response()->json(['error' => 'Equipos no encontrados'], 404);
        }

        return response()->json($equipos);
    }
}
