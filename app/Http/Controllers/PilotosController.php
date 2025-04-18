<?php

namespace App\Http\Controllers;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class PilotosController extends Controller
{

    public function index(): Response
    {
        return Inertia::render('Pilotos');
    }

    // Método para obtener los detalles de un piloto específico por su ID
    public function verPiloto($year,$id)
    {
        // Realiza una solicitud HTTP GET a la API de Ergast para obtener los detalles del piloto
        $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}/drivers/{$id}/results.json");
        
        // Si la solicitud es exitosa, extrae los datos del piloto
        if ($response->successful()) {
            $data = $response->json();
            $piloto = $data['MRData']['RaceTable']['Races'] ?? null;
        } else {
            // Si la solicitud falla, devuelve un error 404
            return response()->json(['error' => 'Piloto no encontrado'], 404);
        }

        // Devuelve los detalles del piloto en formato JSON
        return response()->json($piloto);
    }

    private function obtenerPilotosPorAnho($year)
    {
        $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}/drivers.json");

        $resultado = null;

        if ($response->successful()) {
            $resultado = $response->json()['MRData']['DriverTable']['Drivers'] ?? [];
        }

        return $resultado;
    }

    // Método para listar las carreras en las que participó un piloto en un año específico
    public function PilotosPorAnho($year)
    {
        $pilotos = $this->obtenerPilotosPorAnho($year);
        return response()->json($pilotos ?? []);
    }

    public function calificacionesActuales()
    {
    $year = date('Y');
    $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}/driverstandings.json");

    if ($response->successful()) {
        $data = $response->json();
        $resultados = $data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'] ?? [];
    }

    return response()->json($resultados);
    }
}