<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Piloto;


class PilotosTableSeeder extends Seeder
{
    public function run()
    {
        $pilotos = [
            ['driver_id' => 'albon', 'nombre' => 'Alexander Albon', 'precio' => 20000000],
            ['driver_id' => 'alonso', 'nombre' => 'Fernando Alonso', 'precio' => 35000000],
            ['driver_id' => 'antonelli', 'nombre' => 'Andrea Kimi Antonelli', 'precio' => 15000000],
            ['driver_id' => 'bearman', 'nombre' => 'Oliver Bearman', 'precio' => 18000000],
            ['driver_id' => 'bortoleto', 'nombre' => 'Gabriel Bortoleto', 'precio' => 12000000],
            ['driver_id' => 'doohan', 'nombre' => 'Jack Doohan', 'precio' => 25000000],
            ['driver_id' => 'gasly', 'nombre' => 'Pierre Gasly', 'precio' => 30000000],
            ['driver_id' => 'hadjar', 'nombre' => 'Isack Hadjar', 'precio' => 14000000],
            ['driver_id' => 'hamilton', 'nombre' => 'Lewis Hamilton', 'precio' => 50000000],
            ['driver_id' => 'hulkenberg', 'nombre' => 'Nico Hülkenberg', 'precio' => 22000000],
            ['driver_id' => 'lawson', 'nombre' => 'Liam Lawson', 'precio' => 16000000],
            ['driver_id' => 'leclerc', 'nombre' => 'Charles Leclerc', 'precio' => 40000000],
            ['driver_id' => 'norris', 'nombre' => 'Lando Norris', 'precio' => 32000000],
            ['driver_id' => 'ocon', 'nombre' => 'Esteban Ocon', 'precio' => 28000000],
            ['driver_id' => 'piastri', 'nombre' => 'Oscar Piastri', 'precio' => 26000000],
            ['driver_id' => 'russell', 'nombre' => 'George Russell', 'precio' => 38000000],
            ['driver_id' => 'sainz', 'nombre' => 'Carlos Sainz', 'precio' => 37000000],
            ['driver_id' => 'stroll', 'nombre' => 'Lance Stroll', 'precio' => 24000000],
            ['driver_id' => 'tsunoda', 'nombre' => 'Yuki Tsunoda', 'precio' => 20000000],
            ['driver_id' => 'max_verstappen', 'nombre' => 'Max Verstappen', 'precio' => 45000000 ],
        ];

        foreach ($pilotos as $piloto) {
            Piloto::create($piloto);
        }
    }
}