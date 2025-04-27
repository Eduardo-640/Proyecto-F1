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
        Schema::create('usuario_piloto', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('user_id'); // Relación con la tabla usuarios
            $table->unsignedBigInteger('piloto_id'); // Relación con la tabla pilotos
            $table->boolean('seleccionado')->default(false); // Indica si el piloto está seleccionado para jugar
            $table->timestamps();

            // Claves foráneas
            $table->foreign('user_id')->references('id')->on('usuarios')->onDelete('cascade');
            $table->foreign('piloto_id')->references('id')->on('pilotos')->onDelete('cascade');

            // Evitar duplicados
            $table->unique(['user_id', 'piloto_id']);
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('usuario_piloto');
    }
};