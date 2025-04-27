<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use Illuminate\Support\Facades\Http;

class EquiposControllerTest extends TestCase
{
    public function test_index()
    {
        $response = $this->get('/equipos');

        $response->assertStatus(200);
        $response->assertSee('Equipos');
    }

    public function test_obtener_equipos()
    {
        Http::fake([
            'https://api.jolpi.ca/ergast/f1/*' => Http::response(['MRData' => ['ConstructorTable' => ['Constructors' => []]]], 200),
        ]);

        $response = $this->getJson('/api/equipos/2025');

        $response->assertStatus(200);
        $response->assertJson([]);
    }
}