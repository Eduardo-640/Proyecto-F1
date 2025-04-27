<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use Illuminate\Support\Facades\Http;

class CarrerasControllerTest extends TestCase
{
    public function test_index()
    {
        $response = $this->get('/carreras');

        $response->assertStatus(200);
        $response->assertSee('Carreras');
    }

    public function test_obtener_carreras()
    {
        Http::fake([
            'https://api.jolpi.ca/ergast/f1/2025.json' => Http::response(['MRData' => ['RaceTable' => ['Races' => []]]], 200),
        ]);

        $response = $this->getJson('/api/carreras/2025');

        $response->assertStatus(200);
        $response->assertJson([]);
    }

    public function test_ver_carrera()
    {
        Http::fake([
            'https://api.jolpi.ca/ergast/f1/2025/1.json' => Http::response(['MRData' => ['RaceTable' => ['Races' => [['Results' => []]]]]], 200),
            'https://api.jolpi.ca/ergast/f1/2025/1/results.json' => Http::response(['MRData' => ['RaceTable' => ['Races' => [['Results' => []]]]]], 200),
        ]);

        $response = $this->getJson('/api/carrera/2025/1');

        $response->assertStatus(200);
        $response->assertJsonStructure(['detalles', 'resultados']);
    }
}