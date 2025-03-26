<?php

namespace App\Http\Controllers;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class CarrerasController extends Controller
{
    // Método para renderizar la vista principal de carreras
    public function index(): Response
    {
        return Inertia::render('Carreras');
    }

    // Método para obtener las carreras de un año específico
    public function obtenerCarreras($year)
    {
        // Realiza una solicitud HTTP GET a la API de Ergast para obtener las carreras del año especificado
        $response = Http::get("https://ergast.com/api/f1/{$year}.json");

        // Si la solicitud es exitosa, extrae los datos de las carreras
        if ($response->successful()) {
            $data = $response->json();
            $carreras = $data['MRData']['RaceTable']['Races'] ?? [];
        } else {
            // Si la solicitud falla, establece un array vacío para las carreras
            $carreras = [];
        }

        // Devuelve las carreras en formato JSON
        return response()->json($carreras);
    }

    // Método para obtener los detalles de una carrera específica por su ID
    public function verCarrera($year, $round)
    {
        // Diccionario de URLs de la API que necesitas consultar
        $urls = [
            'detalles' => "https://ergast.com/api/f1/{$year}/{$round}.json",
            'resultados' => "https://ergast.com/api/f1/{$year}/{$round}/results.json", // resultados de la carrera
            //'calendario' => "https://ergast.com/api/f1/{$year}.json", // calendario de la temporada
            //'pilotos' => "https://ergast.com/api/f1/{$year}/{$round}/drivers.json", // lista de pilotos
            //'driverStandings' => "https://ergast.com/api/f1/{$year}/{$round}/driverStandings.json", // clasificacion de pilotos
            //'constructorStandings' => "https://ergast.com/api/f1/{$year}/{$round}/constructorStandings.json", // clasificacion de constructores
            // 'fastestLaps' => "https://ergast.com/api/f1/{$year}/{$round}/fastest/1/laps.json",
        ];

        $resultados = [];

        // Realiza las solicitudes HTTP GET a cada URL en el diccionario
        foreach ($urls as $key => $url) {
            $response = Http::get($url);

            // Si la solicitud no es exitosa, devuelve un error 404
            if (!$response->successful()) {
                return response()->json(['error' => 'Carrera no encontrada'], 404);
            }

            // Extrae los datos de la respuesta y agrégalos al diccionario de resultados
            $data = $response->json();
            //$resultados[$key] = $data['MRData']['RaceTable']['Races'][0] ?? null;

            if ($key === 'resultados') {
                $resultados[$key] = $data['MRData']['RaceTable']['Races'][0]['Results'] ?? [];
            } else {
                $resultados[$key] = $data['MRData']['RaceTable']['Races'][0] ?? null;
            }

        }

        // Devuelve todos los resultados en formato JSON
        return response()->json($resultados);
    }
}