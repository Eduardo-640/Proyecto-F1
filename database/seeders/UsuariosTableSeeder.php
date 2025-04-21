<?php

namespace Database\Seeders;

use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class UsuariosTableSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        //
        DB::table('usuarios')->insert([
            'name' => 'prueba',
            'email' => 'prueba@gmail.com',
            'password' => Hash::make('1234'),
            'profile_photo' => 'foto_de_perfil.jpg', 
            'email_verified_at' => now(),
        ]);
    }
}
