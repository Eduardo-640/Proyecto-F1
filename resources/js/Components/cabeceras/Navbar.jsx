import { Link, usePage } from "@inertiajs/react";
import { useState } from "react";

export default function Navbar() {
  const { auth } = usePage().props;
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  return (
    <header className="sticky top-0 z-50 bg-black/90 backdrop-blur-sm border-b border-red-600">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center">
          <Link href="/" className="text-white flex items-center font_enlaces">
            <img src="/favicon-32x32.png" alt="Icono F1" />
            <span className="hidden sm:inline text-xl font-semibold">FORMULA 1</span>
          </Link>
        </div>

        {/* Barra Navegación */}
        <nav className="hidden md:flex items-center space-x-8">
          <Link href="/" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">
            INICIO
          </Link>
          <Link href="/pilotos" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">
            PILOTOS
          </Link>
          <Link href="/equipos" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">
            EQUIPOS
          </Link>
          <Link href="/carreras" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">
            CARREAS
          </Link>
          <Link href="/noticias" className="text-white text-sm font-medium hover:text-red-500 transition-colors font_enlaces">
            NOTICIAS
          </Link>
        </nav>

        <div className="flex items-center gap-4 relative">
          {!auth.user ? (
            <Link href="/login" className="hidden sm:flex border border-danger text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded-md font_enlaces">
              SIGN IN
            </Link>
          ) : (
            <div className="flex items-center gap-2 cursor-pointer" onClick={toggleDropdown}>
              <img
                src={auth.user.profile_photo_url || "/images/default-profile.png"}
                alt="Foto de perfil"
                className="w-8 h-8 rounded-full"
              />
              <span className="text-white text-sm font-medium">{auth.user.name}</span>
              {dropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-2 z-50">
                  <Link
                    href="/perfil"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Perfil
                  </Link>
                  <Link
                    href="/logout"
                    method="post"
                    className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                  >
                    Cerrar sesión
                  </Link>
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
