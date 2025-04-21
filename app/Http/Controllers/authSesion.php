<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Models\User; 

class authSesion extends Controller
{
    public function login(Request $request)
    {
        $request->validate([
            'email' => 'required|email',
            'password' => 'required',
        ]);

        if (Auth::attempt(['email' => $request->input('email'), 'password' => $request->input('password')])) {
            $request->session()->regenerate();
            return redirect('/')->with('success', 'Inicio de sesión exitoso.');
        }

        return back()->withErrors(['email' => 'Estas credenciales no coinciden con nuestros registros.']);
    }

    public function logout(Request $request)
    {
        $request->session()->forget('user');
        return redirect('/login')->with('success', 'Sesión cerrada correctamente.');
    }
}