import '../css/app.css';
import '../css/global.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap';

import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Pages
import Home       from './Pages/Home';
import Pilotos    from './Pages/Pilotos';
import Equipos    from './Pages/Equipos';
import Carreras   from './Pages/Carreras';
import Noticias   from './Pages/Noticias';
import Perfil     from './Pages/Perfil';
import Dashboard  from './Pages/Dashboard';
import Welcome    from './Pages/Welcome';

// Auth pages
import Login           from './Pages/Auth/Login';
import Register        from './Pages/Auth/Register';
import ForgotPassword  from './Pages/Auth/ForgotPassword';
import ResetPassword   from './Pages/Auth/ResetPassword';
import VerifyEmail     from './Pages/Auth/VerifyEmail';
import ConfirmPassword from './Pages/Auth/ConfirmPassword';

// Fantasy pages
import FantasyIndex  from './Pages/Fantasy/Index';
import CrearEquipo   from './Pages/Fantasy/CrearEquipo';
import MiEquipo      from './Pages/Fantasy/MiEquipo';
import FantasyEquipos from './Pages/Fantasy/Equipos';
import Compra        from './Pages/Fantasy/Compra';
import Venta         from './Pages/Fantasy/Venta';

const mountEl = document.getElementById('app');
const root = createRoot(mountEl);

root.render(
    <BrowserRouter>
        <AuthProvider>
            <Routes>
                <Route path="/"                  element={<Home />} />
                <Route path="/pilotos"           element={<Pilotos />} />
                <Route path="/equipos"           element={<Equipos />} />
                <Route path="/carreras"          element={<Carreras />} />
                <Route path="/noticias"          element={<Noticias />} />
                <Route path="/perfil"            element={<Perfil />} />
                <Route path="/dashboard"         element={<Dashboard />} />
                <Route path="/login"             element={<Login />} />
                <Route path="/register"          element={<Register />} />
                <Route path="/forgot-password"   element={<ForgotPassword />} />
                <Route path="/reset-password"    element={<ResetPassword />} />
                <Route path="/verify-email"      element={<VerifyEmail />} />
                <Route path="/confirm-password"  element={<ConfirmPassword />} />
                <Route path="/fantasy"           element={<FantasyIndex />} />
                <Route path="/fantasy/crear"     element={<CrearEquipo />} />
                <Route path="/fantasy/mi-equipo" element={<MiEquipo />} />
                <Route path="/fantasy/equipos"   element={<FantasyEquipos />} />
                <Route path="/fantasy/compra"    element={<Compra />} />
                <Route path="/fantasy/venta"     element={<Venta />} />
                <Route path="*"                  element={<Welcome />} />
            </Routes>
        </AuthProvider>
    </BrowserRouter>
);
