<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use App\Models\Piloto;
use App\Models\User;

class FantasyControllerTest extends TestCase
{
    public function test_index()
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        $response = $this->get('/fantasy');

        $response->assertStatus(200);
        $response->assertSee('Fantasy');
    }

    public function test_get_pilotos()
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        Piloto::factory()->count(3)->create(['disponible' => true]);

        $response = $this->getJson('/fantasy/pilotos');

        $response->assertStatus(200);
        $response->assertJsonCount(3);
    }

    public function test_comprar_piloto()
    {
        $user = User::factory()->create(['presupuesto' => 100]);
        $this->actingAs($user);

        $piloto = Piloto::factory()->create(['precio' => 50, 'disponible' => true]);

        $response = $this->postJson('/fantasy/comprar-piloto', ['piloto_id' => $piloto->id]);

        $response->assertStatus(200);
        $response->assertJson(['message' => 'Piloto comprado exitosamente.']);

        $this->assertDatabaseHas('usuario_piloto', [
            'user_id' => $user->id,
            'piloto_id' => $piloto->id,
        ]);

        $this->assertEquals(50, $user->fresh()->presupuesto);
    }

    // Test para vender un piloto
    public function test_vender_piloto()
    {
        $user = User::factory()->create(['presupuesto' => 100]);
        $this->actingAs($user);

        $piloto = Piloto::factory()->create(['precio' => 50, 'disponible' => false]);

        // Asignar el piloto al usuario
        $user->pilotos()->attach($piloto->id);

        $response = $this->postJson('/fantasy/vender-piloto', ['piloto_id' => $piloto->id]);

        $response->assertStatus(200);
        $response->assertJson(['message' => 'Piloto vendido exitosamente.']);

        // Verificar que el piloto se haya desasociado y que el presupuesto aumente
        $this->assertDatabaseMissing('usuario_piloto', [
            'user_id' => $user->id,
            'piloto_id' => $piloto->id,
        ]);

        $this->assertEquals(150, $user->fresh()->presupuesto);
    }

    // Test para obtener el equipo del usuario
    public function test_mi_equipo()
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        // Crear pilotos y asignarlos al usuario
        $piloto1 = Piloto::factory()->create();
        $piloto2 = Piloto::factory()->create();

        $user->pilotos()->attach([$piloto1->id, $piloto2->id]);

        // Verificar que los pilotos se devuelvan correctamente en el equipo
        $response = $this->getJson('/fantasy/mi-equipo');

        $response->assertStatus(200);
        $response->assertJsonCount(2);
        $response->assertJsonFragment(['id' => $piloto1->id]);
        $response->assertJsonFragment(['id' => $piloto2->id]);
    }
}
