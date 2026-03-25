import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
  const { user: authUser, logout } = useAuth();
  const auth = { user: authUser ?? null };
  const [dropdownOpen, setDropdownOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-red-600 bg-black/90 backdrop-blur-sm">
      <div className="container mx-auto flex items-center justify-between px-4 py-3">
        <div className="flex items-center">
          <Link to="/" className="font_enlaces flex items-center text-white">
            <img src="/favicon-32x32.png" alt="Icono F1" />
            <span className="hidden text-xl font-semibold sm:inline">
              FORMULA 1
            </span>
          </Link>
        </div>

        <nav className="hidden items-center space-x-8 md:flex">
          <Link
            to="/"
            className="font_enlaces text-sm font-medium text-white transition-colors hover:text-red-500"
          >
            INICIO
          </Link>
          <Link
            to="/pilotos"
            className="font_enlaces text-sm font-medium text-white transition-colors hover:text-red-500"
          >
            PILOTOS
          </Link>
          <Link
            to="/equipos"
            className="font_enlaces text-sm font-medium text-white transition-colors hover:text-red-500"
          >
            EQUIPOS
          </Link>
          <Link
            to="/carreras"
            className="font_enlaces text-sm font-medium text-white transition-colors hover:text-red-500"
          >
            CARRERAS
          </Link>
          <Link
            to="/analytics"
            className="font_enlaces text-sm font-medium text-white transition-colors hover:text-red-500"
          >
            ANALYTICS
          </Link>
          <Link
            to="/noticias"
            className="font_enlaces text-sm font-medium text-white transition-colors hover:text-red-500"
          >
            NOTICIAS
          </Link>
          {auth.user && (
            <Link
              to="/fantasy"
              className="font_enlaces text-sm font-medium text-white transition-colors hover:text-red-500"
            >
              MANAGER F1
            </Link>
          )}
        </nav>

        <div className="relative flex items-center gap-4">
          {!auth.user ? (
            <Link
              to="/login"
              className="font_enlaces hidden rounded-md border border-red-600 px-4 py-2 text-red-600 hover:bg-red-600 hover:text-white sm:flex"
            >
              SIGN IN
            </Link>
          ) : (
            <div
              className="relative flex cursor-pointer items-center gap-2"
              onClick={() => setDropdownOpen(!dropdownOpen)}
            >
              <img
                src={
                  auth.user.profile_photo_url || '/images/imagen_respaldo.png'
                }
                alt="Foto de perfil"
                className="h-8 w-8 rounded-full"
              />
              <span className="text-sm font-medium text-white">
                {auth.user.name}
              </span>
              {dropdownOpen && (
                <div className="absolute right-0 top-10 z-50 w-48 rounded-md bg-white py-2 shadow-lg">
                  <Link
                    to="/perfil"
                    className="font_enlaces block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Perfil
                  </Link>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      logout();
                    }}
                    className="block w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Cerrar sesión
                  </button>
                </div>
              )}
            </div>
          )}
          <button className="hidden rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700 sm:flex">
            SUSCRIBIRSE
          </button>
        </div>
      </div>
    </header>
  );
}
