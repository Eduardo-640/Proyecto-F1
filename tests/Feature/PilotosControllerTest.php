<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use Illuminate\Support\Facades\Http;

class PilotosControllerTest extends TestCase
{
    public function test_index()
    {
        $response = $this->get('/pilotos');

        $response->assertStatus(200);
        $response->assertSee('Pilotos');
    }

    public function test_ver_piloto()
    {
        Http::fake([
            'https://api.jolpi.ca/ergast/f1/2025/drivers/1/results.json' => Http::response(['MRData' => ['RaceTable' => ['Races' => []]]], 200),
        ]);

        $response = $this->getJson('/api/pilotos/2025/detalles/1');

        $response->assertStatus(200);
        $response->assertJson([]);
    }

    public function test_pilotos_por_anho()
    {
        Http::fake([
            'https://api.jolpi.ca/ergast/f1/2025/drivers.json' => Http::response(['MRData' => ['DriverTable' => ['Drivers' => []]]], 200),
        ]);

        $response = $this->getJson('/api/pilotos/2025');

        $response->assertStatus(200);
        $response->assertJson([]);
    }
}