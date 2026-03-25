import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Pages
import Analytics from './Pages/Analytics';
import Carreras from './Pages/Carreras';
import Dashboard from './Pages/Dashboard';
import Equipos from './Pages/Equipos';
import Home from './Pages/Home';
import Noticias from './Pages/Noticias';
import Perfil from './Pages/Perfil';
import Pilotos from './Pages/Pilotos';
import Welcome from './Pages/Welcome';

// Auth pages
import ConfirmPassword from './Pages/Auth/ConfirmPassword';
import ForgotPassword from './Pages/Auth/ForgotPassword';
import Login from './Pages/Auth/Login';
import Register from './Pages/Auth/Register';
import ResetPassword from './Pages/Auth/ResetPassword';
import VerifyEmail from './Pages/Auth/VerifyEmail';

// Fantasy pages
import Compra from './Pages/Fantasy/Compra';
import CrearEquipo from './Pages/Fantasy/CrearEquipo';
import FantasyEquipos from './Pages/Fantasy/Equipos';
import FantasyIndex from './Pages/Fantasy/Index';
import MiEquipo from './Pages/Fantasy/MiEquipo';
import Venta from './Pages/Fantasy/Venta';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/pilotos" element={<Pilotos />} />
          <Route path="/equipos" element={<Equipos />} />
          <Route path="/carreras" element={<Carreras />} />
          <Route path="/noticias" element={<Noticias />} />
          <Route path="/perfil" element={<Perfil />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-email" element={<VerifyEmail />} />
          <Route path="/confirm-password" element={<ConfirmPassword />} />
          <Route path="/fantasy" element={<FantasyIndex />} />
          <Route path="/fantasy/crear" element={<CrearEquipo />} />
          <Route path="/fantasy/mi-equipo" element={<MiEquipo />} />
          <Route path="/fantasy/equipos" element={<FantasyEquipos />} />
          <Route path="/fantasy/compra" element={<Compra />} />
          <Route path="/fantasy/venta" element={<Venta />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="*" element={<Welcome />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
