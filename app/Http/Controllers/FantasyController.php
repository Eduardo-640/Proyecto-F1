<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\Request;
use Inertia\Inertia;
use App\Models\Piloto;
use Illuminate\Support\Facades\Auth;
use App\Models\User;

class FantasyController extends Controller
{
    public function index()
    {
        return Inertia::render('Fantasy/Index');
    }

    public function getPilotos()
    {
        $user = Auth::user();

        // Obtener pilotos que no han sido comprados por ningún usuario
        $pilotos = Piloto::where('disponible', true)->get();

        return response()->json($pilotos);
    }

    public function comprarPiloto(Request $request)
    {
        $request->validate([
            'piloto_id' => 'required|exists:pilotos,id',
        ]);

        $piloto = Piloto::findOrFail($request->piloto_id);

        if (!$piloto->disponible) {
            return response()->json(['message' => 'Este piloto ya ha sido comprado.'], 400);
        }

        $user = Auth::user();

        if ($user->presupuesto < $piloto->precio) {
            return response()->json(['message' => 'No tienes suficiente presupuesto para comprar este piloto.'], 400);
        }

        // Reducir el presupuesto del usuario
        $user->presupuesto -= $piloto->precio;
        $user->save();

        // Asociar el piloto al usuario
        $user->pilotos()->attach($piloto->id);

        // Marcar el piloto como no disponible
        $piloto->disponible = false;
        $piloto->save();

        return response()->json(['message' => 'Piloto comprado exitosamente.']);
    }

    public function venderPiloto(Request $request)
    {
        $request->validate([
            'piloto_id' => 'required|exists:pilotos,id',
        ]);

        $user = Auth::user();
        $piloto = $user->pilotos()->find($request->piloto_id);

        if (!$piloto) {
            return response()->json(['message' => 'No posees este piloto.'], 400);
        }

        // Eliminar la relación entre el usuario y el piloto
        $user->pilotos()->detach($piloto->id);

        // Sumar el precio del piloto al presupuesto del usuario
        $user->presupuesto += $piloto->precio;
        $user->save();

        // Marcar el piloto como disponible
        $piloto->disponible = true;
        $piloto->save();

        return response()->json(['message' => 'Piloto vendido exitosamente.']);
    }

    public function miEquipo()
    {
        $user = Auth::user();
        $pilotos = $user->pilotos()->withPivot('seleccionado')->get();

        return response()->json($pilotos);
    }

    public function seleccionarPiloto(Request $request)
    {
        $request->validate([
            'piloto_id' => 'required|exists:pilotos,id',
            'seleccionado' => 'required|boolean',
        ]);

        $user = Auth::user();
        $piloto = $user->pilotos()->find($request->piloto_id);

        if (!$piloto) {
            return response()->json(['message' => 'No posees este piloto.'], 400);
        }

        // Verificar que no haya más de dos pilotos seleccionados
        if ($request->seleccionado && $user->pilotos()->wherePivot('seleccionado', true)->count() >= 2) {
            return response()->json(['message' => 'Solo puedes seleccionar dos pilotos para jugar.'], 400);
        }

        // Actualizar el estado de selección del piloto
        $user->pilotos()->updateExistingPivot($piloto->id, ['seleccionado' => $request->seleccionado]);

        return response()->json(['message' => 'Estado de selección actualizado exitosamente.']);
    }

    public function equipos()
    {
        $year = date('Y');
        $response = Http::get("https://api.jolpi.ca/ergast/f1/{$year}/driverstandings.json");

        $resultados = [];
        if ($response->successful()) {
            $data = $response->json();
            $resultados = $data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'] ?? [];
        } else {
            // Registrar error si la API falla
            \Log::error('Error al obtener datos de la API de Ergast', ['response' => $response->body()]);
            return response()->json(['error' => 'No se pudieron obtener los datos de la API'], 500);
        }

        // Verificar los datos obtenidos de la API
        \Log::info('Datos de la API obtenidos', ['resultados' => $resultados]);

        // Obtener los usuarios con sus pilotos seleccionados
        $usuarios = User::with(['pilotos' => function ($query) {
            $query->wherePivot('seleccionado', true);
        }])->get();

        // Verificar los usuarios y pilotos seleccionados
        \Log::info('Usuarios y pilotos seleccionados', ['usuarios' => $usuarios]);

        // Calcular los puntos de los usuarios basados en los puntos de los pilotos seleccionados
        $usuarios->each(function ($usuario) use ($resultados) {
            $usuario->puntos = 0;

            foreach ($usuario->pilotos as $piloto) {
                // Buscar los puntos del piloto en las calificaciones actuales
                $calificacion = collect($resultados)->firstWhere('Driver.driverId', $piloto->driver_id);

                if ($calificacion) {
                    $usuario->puntos += $calificacion['points'];
                } else {
                    // Registrar si no se encuentra el piloto en los resultados
                    \Log::warning('Piloto no encontrado en los resultados', ['driver_id' => $piloto->driver_id]);
                }
            }
        });

        // Verificar los puntos calculados
        \Log::info('Puntos calculados para los usuarios', ['usuarios' => $usuarios]);

        return response()->json($usuarios);
    }

    public function obtenerPresupuesto()
    {
        $user = Auth::user();
        return response()->json(['presupuesto' => $user->presupuesto]);
    }
}
