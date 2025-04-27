<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;
use App\Models\User;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

class PerfilControllerTest extends TestCase
{
    public function test_index()
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        $response = $this->get('/perfil');

        $response->assertStatus(200);
        $response->assertSee('Perfil');
    }

    public function test_update()
    {
        $user = User::factory()->create();
        $this->actingAs($user);

        $response = $this->put('/perfil', [
            'name' => 'Nuevo Nombre',
            'email' => 'nuevoemail@example.com',
            'password' => 'nueva_contraseña',
        ]);

        $response->assertStatus(200);
        $this->assertEquals('Nuevo Nombre', $user->fresh()->name);
        $this->assertEquals('nuevoemail@example.com', $user->fresh()->email);
    }

    // public function test_destroy()
    // {
    //     $user = User::factory()->create();
    //     $this->actingAs($user);

    //     $response = $this->delete('/perfil', [
    //         'password' => 'password',
    //     ]);

    //     $response->assertRedirect('/');
    //     $this->assertGuest();
    //     $this->assertDatabaseMissing('users', ['id' => $user->id]);
    // }
}