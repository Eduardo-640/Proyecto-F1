<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Piloto extends Model
{
    use HasFactory;

    protected $fillable = ['nombre', 'precio'];

    // Relación con los usuarios que han comprado este piloto
    public function usuarios(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'usuario_piloto');
    }

    public function scopeSeleccionados($query)
    {
        return $query->wherePivot('seleccionado', true);
    }
}
