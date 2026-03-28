import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useState } from "react";

export default function Navbar() {
  const { user: authUser, logout } = useAuth();
  const auth = { user: authUser ?? null };
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 bg-black/90 backdrop-blur-sm border-b border-red-600">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center">
          <Link to="/" className="text-white flex items-center font_enlaces">
            <img src="/favicon-32x32.png" alt="Icono F1" />
            <span className="hidden sm:inline text-xl font-semibold">FORMULA 1</span>
          </Link>
        </div>

        <nav className="hidden md:flex items-center space-x-8">
          <Link to="/" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">INICIO</Link>
          <Link to="/drivers" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">PILOTOS</Link>
          <Link to="/teams" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">EQUIPOS</Link>
          <Link to="/races" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">CARRERAS</Link>
          <Link to="/news" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">NOTICIAS</Link>
          {auth.user && (
            <Link to="/fantasy" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">MANAGER F1</Link>
          )}
        </nav>

        <div className="flex items-center gap-4 relative">
          {!auth.user ? (
            <Link to="/login" className="hidden sm:flex border border-red-600 text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded-md font_enlaces">
              SIGN IN
            </Link>
          ) : (
            <div className="flex items-center gap-2 cursor-pointer relative" onClick={() => setDropdownOpen(!dropdownOpen)}>
              <img
                src={auth.user.profile_photo_url || "/images/imagen_respaldo.png"}
                alt="Foto de perfil"
                className="w-8 h-8 rounded-full"
              />
              <span className="text-white text-sm font-medium">{auth.user.name}</span>
              {dropdownOpen && (
                <div className="absolute right-0 top-10 w-48 bg-white rounded-md shadow-lg py-2 z-50">
                  <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 font_enlaces">
                    Perfil
                  </Link>
                  <button
                    onClick={(e) => { e.stopPropagation(); logout(); }}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Cerrar sesión
                  </button>
                </div>
              )}
            </div>
          )}
          <button className="hidden sm:flex bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md">
            SUSCRIBIRSE
          </button>
        </div>
      </div>
    </header>
  );
}
