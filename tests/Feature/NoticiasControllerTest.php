<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use Illuminate\Support\Facades\Http;

class NoticiasControllerTest extends TestCase
{
    public function test_index()
    {
        $response = $this->get('/noticias');

        $response->assertStatus(200);
        $response->assertSee('Noticias');
    }

    public function test_obtener_noticias()
    {
        Http::fake([
            'https://newsapi.org/v2/everything*' => Http::response(['articles' => []], 200),
        ]);

        $response = $this->getJson('/api/noticias');

        $response->assertStatus(200);
        $response->assertJson([]);
    }
}