<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('equipo_piloto', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('equipo_id'); // Relación con la tabla equipos
            $table->unsignedBigInteger('piloto_id'); // Relación con la tabla pilotos
            $table->timestamps();

            // Claves foráneas
            $table->foreign('equipo_id')->references('id')->on('equipos')->onDelete('cascade');
            $table->foreign('piloto_id')->references('id')->on('pilotos')->onDelete('cascade');

            // Evitar duplicados en la relación
            $table->unique(['equipo_id', 'piloto_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('equipo_piloto');
    }
};
