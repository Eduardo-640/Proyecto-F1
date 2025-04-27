<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Equipo extends Model
{
    use HasFactory;

    protected $fillable = [
        'nombre',
        'user_id',
        'presupuesto',
    ];

    // Relación con el modelo User
    // (uno a muchos)
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    // Relación con los pilotos 
    // (muchos a muchos)
    public function pilotos()
    {
        return $this->belongsToMany(Piloto::class, 'equipo_piloto');
    }
}
