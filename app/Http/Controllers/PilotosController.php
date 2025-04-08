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
        $response = Http::get("https://ergast.com/api/f1/{$year}/drivers/{$id}/results.json");
        
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

    // Método para listar las carreras en las que participó un piloto en un año específico
    public function PilotosPorAnho($year)
    {
        // Realiza una solicitud HTTP GET a la API de Ergast para obtener las carreras del piloto
        $response = Http::get("https://ergast.com/api/f1/{$year}/drivers.json");

        // Si la solicitud es exitosa, extrae los datos de las carreras
        if ($response->successful()) {
            $data = $response->json();
            $carreras = $data['MRData']['DriverTable']['Drivers'] ?? [];
        } else {
            // Si la solicitud falla, establece un array vacío para las carreras
            $carreras = [];
        }

        // Devuelve las carreras en formato JSON
        return response()->json($carreras);
    }
}