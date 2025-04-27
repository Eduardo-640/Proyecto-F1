<?php

namespace Tests\Feature;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class HomeControllerTest extends TestCase
{
    public function test_index()
    {
        $response = $this->get('/');

        $response->assertStatus(200);
        $response->assertSee('Home');
    }
}