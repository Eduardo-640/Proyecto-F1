<?php
namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Inertia\Inertia;

class PerfilController extends Controller
{
    
    //Muestra la página de perfil del usuario autenticado.
    public function index()
    {
        return Inertia::render('Perfil');
    }

    
    //Actualiza la información del perfil del usuario autenticado.
    public function update(Request $request)
    {
        $user = $request->user();

        $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|max:255|unique:users,email,' . $user->id,
        ]);

        $user->update($request->only('name', 'email'));

        return redirect()->route('perfil')->with('success', 'Perfil actualizado correctamente.');
    }

    
    //Elimina la cuenta del usuario autenticado.
    public function destroy(Request $request)
    {
        $user = $request->user();

        $request->validate([
            'password' => 'required|current_password',
        ]);

        $user->delete();

        auth()->logout();

        return redirect('/')->with('success', 'Cuenta eliminada correctamente.');
    }
}