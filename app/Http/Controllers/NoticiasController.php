<?php

namespace App\Http\Controllers;
use Inertia\Inertia;
use Inertia\Response;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class NoticiasController extends Controller
{
    //
    public function index(): Response
    {
        return Inertia::render('Noticias');
    }

    // Método para obtener todas las noticias desde una API
    public function obtenerNoticias()
    {
        // URL de la API para obtener las noticias
        // que tengan la palabra "F1" en el título
        // y que sean de los dominios especificados (marca.com, diariomotor.com, mundodeportivo.com)
        // y que estén en español
        // y que sean 2 semanas atras de la fecha especificada
        // y que estén ordenadas por fecha de publicación
        $url = "https://newsapi.org/v2/everything?q=F1&from=2025-04-01&sortBy=publishedAt&apiKey=67d19be62e9043b8939703d6d3ae08c4&language=es&domains=marca.com,diariomotor.com,mundodeportivo.com";

        // Realiza una solicitud HTTP GET a la API
        $response = Http::get($url);

        // Si la solicitud es exitosa, extrae los datos de las noticias
        if ($response->successful()) {
            $noticias = $response->json();
        } else {
            // Si la solicitud falla, devuelve un error 404
            return response()->json(['error' => 'No se pudieron obtener las noticias'], 404);
        }

        // Devuelve las noticias en formato JSON
        return response()->json($noticias);
    }
}
