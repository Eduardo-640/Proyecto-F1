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
        Schema::create('pilotos', function (Blueprint $table) {
            $table->id();
            $table->timestamps();
            $table->string('nombre')->nullable(); // Nombre del piloto
            $table->string('driver_id')->nullable(); // ID del piloto
            $table->decimal('precio', 10, 0); // Precio del piloto
            $table->boolean('disponible')->default(true); // Indica si el piloto está disponible para la compra
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('pilotos');
    }
};
