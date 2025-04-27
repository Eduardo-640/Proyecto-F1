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
        Schema::create('equipos', function (Blueprint $table) {
            $table->id();
            $table->string('nombre'); // Nombre del equipo
            $table->unsignedBigInteger('user_id'); // Relación con el usuario que creó el equipo
            $table->decimal('presupuesto', 15, 2); // Presupuesto del equipo
            $table->timestamps();

            // Clave foránea para el usuario
            $table->foreign('user_id')->references('id')->on('usuarios')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('equipos');
    }
};
