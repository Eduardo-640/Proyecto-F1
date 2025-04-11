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
        $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}.json");

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
            'detalles' => "https://api.jolpi.ca/ergast/f1/{$year}/{$round}.json",
            'resultados' => "https://api.jolpi.ca/ergast/f1/{$year}/{$round}/results.json", // resultados de la carrera
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

    // Método para obtener la próxima carrera respecto a la fecha actual
    public function proximaCarrera()
    {
        // Obtener el año actual
        $year = date('Y');

        // Realizar la solicitud HTTP GET a la API para obtener las carreras del año actual
        $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}.json");

        // Inicializar la variable de respuesta
        $resultado = [];

        // Verificar si la solicitud fue exitosa
        if ($response->successful()) {
            // Extraer los datos de las carreras
            $data = $response->json();
            $carreras = $data['MRData']['RaceTable']['Races'] ?? [];

            // Obtener la fecha actual
            $fechaActual = date('Y-m-d');

            // Buscar la próxima carrera
            foreach ($carreras as $carrera) {
                if (isset($carrera['date']) && $carrera['date'] > $fechaActual) {
                    $resultado = $carrera;
                    break;
                }
            }

            // Si no se encuentra una próxima carrera
            if (empty($resultado)) {
                $resultado = ['message' => 'No hay próximas carreras disponibles'];
            }
        } else {
            // Si la solicitud falla
            $resultado = ['error' => 'No se pudieron obtener las carreras'];
        }

        // Devolver el resultado en formato JSON
        return response()->json($resultado, empty($resultado['error']) ? 200 : 500);
    }

    public function calendarioCarreras()
    {
        // Obtener el año actual
        $year = date('Y');

        // Realizar la solicitud HTTP GET a la API para obtener las carreras del año actual
        $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}.json");

        // Inicializar la variable de respuesta
        $resultado = [];

        // Verificar si la solicitud fue exitosa
        if ($response->successful()) {
            // Extraer los datos de las carreras
            $data = $response->json();
            $carreras = $data['MRData']['RaceTable']['Races'] ?? [];

            // Obtener la fecha actual
            $fechaActual = date('Y-m-d');

            // Filtrar las carreras que aún no han pasado usando un bucle foreach
            foreach ($carreras as $carrera) {
                if (isset($carrera['date']) && $carrera['date'] > $fechaActual) {
                    $resultado[] = $carrera;
                }
            }

            // Si no hay carreras futuras, devolver un mensaje
            if (empty($resultado)) {
                $resultado = ['message' => 'No hay carreras futuras disponibles'];
            }
        } else {
            // Si la solicitud falla
            $resultado = ['error' => 'No se pudieron obtener las carreras'];
        }

        // Devolver el resultado en formato JSON
        return response()->json($resultado, empty($resultado['error']) ? 200 : 500);
    }
}