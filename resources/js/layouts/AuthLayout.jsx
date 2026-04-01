import ApplicationLogo from '@/components/ui/ApplicationLogo';
import Dropdown from '@/components/ui/Dropdown';
import NavLink from '@/components/ui/NavLink';
import ResponsiveNavLink from '@/components/ui/ResponsiveNavLink';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useState, useEffect, useRef } from 'react';

export default function AuthenticatedLayout({ header, children }) {
    const { user, logout } = useAuth();
    const location = useLocation();

    const [showingNavigationDropdown, setShowingNavigationDropdown] =
        useState(false);

    const avatarUrl = user?.profile_photo_url || user?.photo_url || null;

    function initials(name) {
        if (!name) return 'U';
        return name
            .split(' ')
            .map((n) => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    }

    // DEV_FAKE_SVG: SVG data for a temporary development avatar (encoded).
    // Remove this constant and the <img id="DEV_FAKE_AVATAR"> element when
    // using real user avatars in production.
    const DEV_FAKE_SVG = encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 24 24"><rect width="100%" height="100%" fill="#374151" rx="12"/><text x="50%" y="55%" font-size="10" fill="#f3f4f6" font-family="Arial, Helvetica, sans-serif" text-anchor="middle" dominant-baseline="middle">DEV</text></svg>');

    // DEV_EXAMPLE_*: valores de ejemplo para desarrollo. Buscar por DEV_EXAMPLE_*
    // y eliminar estos valores cuando se integre con datos reales.
    const DEV_EXAMPLE_EMAIL = 'dev@example.com';
    const DEV_EXAMPLE_NAME = 'Usuario Dev';

    // DEV_NOTIFICATIONS: notificaciones de ejemplo para desarrollo.
    // Eliminar o reemplazar cuando la API de notificaciones esté disponible.
    const DEV_NOTIFICATIONS = [
        { id: 'DEV_NOTIF_1', title: 'Nuevo mensaje', body: 'Tienes un mensaje de equipo.' },
        { id: 'DEV_NOTIF_2', title: 'Pago recibido', body: 'Saldo actualizado en tu cuenta.' },
    ];

    function NotificationsMenu({ notifications = [] }) {
        const [open, setOpen] = useState(false);
        const ref = useRef(null);

        useEffect(() => {
            function onDocClick(e) {
                if (!open) return;
                if (ref.current && !ref.current.contains(e.target)) setOpen(false);
            }
            document.addEventListener('mousedown', onDocClick);
            return () => document.removeEventListener('mousedown', onDocClick);
        }, [open]);

        return (
            <div ref={ref} className="relative">
                <button
                    aria-label="Notificaciones"
                    onClick={() => setOpen((v) => !v)}
                    className="p-2 rounded-md hover:bg-gray-800 focus:outline-none relative"
                >
                    <svg className="w-5 h-5 text-gray-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6 6 0 10-12 0v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                    {/* badge positioned absolute so it doesn't shift the icon */}
                    {notifications.length > 0 && (
                        <span className="absolute -top-1 -right-1 inline-flex items-center justify-center w-5 h-5 text-xs rounded-full bg-red-500 text-white">{notifications.length}</span>
                    )}
                </button>

                {open && (
                    <div className="absolute right-0 mt-2 w-80 bg-gray-800 border border-gray-700 rounded shadow-lg z-50">
                        <div className="p-3 border-b border-gray-700 font-medium">Notificaciones</div>
                        <div className="max-h-64 overflow-auto">
                            {notifications.length === 0 ? (
                                <div className="p-3 text-sm text-gray-400">Sin notificaciones</div>
                            ) : (
                                notifications.map((n) => (
                                    <div key={n.id} className="p-3 hover:bg-gray-900 border-b border-gray-800">
                                        <div className="text-sm font-medium">{n.title}</div>
                                        <div className="text-xs text-gray-400">{n.body}</div>
                                    </div>
                                ))
                            )}
                        </div>
                        <div className="p-2 text-center">
                            <button className="text-sm text-blue-400 hover:underline">Ver todas</button>
                        </div>
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-900 text-gray-100">
            <nav className="border-b border-gray-800 bg-gray-900">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="flex h-16 items-center justify-between">
                        <div className="flex items-center gap-4">
                            <Link to="/" className="flex items-center gap-3">
                                <ApplicationLogo className="block h-9 w-auto fill-current text-white" />
                                <span className="hidden sm:inline text-lg font-semibold text-white">Proyecto F1</span>
                            </Link>
                        </div>

                        <div className="flex items-center gap-4">
                            {/* Se removió el enlace directo a Dashboard para evitar apariencia de 'link' en el header */}

                            <div className="relative flex items-center">
                                {/* Notificaciones: botón con mini-modal */}
                                <div className="me-3">
                                    <NotificationsMenu notifications={DEV_NOTIFICATIONS} />
                                </div>
                                <Dropdown>
                                    <Dropdown.Trigger>
                                        <button className="inline-flex items-center gap-2 rounded-full focus:outline-none">
                                            {/* Texto a la izquierda del avatar: email encima del nombre (visible en >= sm) */}
                                            <div className="hidden sm:flex flex-col text-right mr-2">
                                                {/* DEV_EXAMPLE_EMAIL: eliminar en producción si no se necesita */}
                                                <span id="DEV_EXAMPLE_EMAIL" className="text-xs text-gray-400">{user?.email ?? DEV_EXAMPLE_EMAIL}</span>
                                                {/* DEV_EXAMPLE_NAME: eliminar en producción si no se necesita */}
                                                <span id="DEV_EXAMPLE_NAME" className="text-sm font-medium text-gray-100">{user?.name ?? DEV_EXAMPLE_NAME}</span>
                                            </div>
                                            {avatarUrl ? (
                                                <img src={avatarUrl} alt="avatar" className="h-9 w-9 rounded-full object-cover" />
                                            ) : (
                                                <>
                                                    {/* DEV_FAKE_AVATAR: Avatar ficticio de desarrollo.
                                                        Elimina la siguiente imagen (elemento con id="DEV_FAKE_AVATAR")
                                                        cuando ya tengas avatares reales o en producción. */}
                                                    <img
                                                        id="DEV_FAKE_AVATAR"
                                                        src={`data:image/svg+xml;utf8,${DEV_FAKE_SVG}`}
                                                        alt="avatar-falso"
                                                        className="h-9 w-9 rounded-full object-cover"
                                                    />
                                                    <div className="sr-only">Avatar de desarrollo (eliminar en producción)</div>
                                                </>
                                            )}
                                        </button>
                                    </Dropdown.Trigger>

                                    {user ? (
                                        <Dropdown.Content className="bg-gray-800 text-gray-100">
                                            <Dropdown.Link to="/profile">Perfil</Dropdown.Link>
                                            <Dropdown.Link href="#" as="button" onClick={(e) => { e.preventDefault(); logout(); }}>Cerrar sesión</Dropdown.Link>
                                        </Dropdown.Content>
                                    ) : (
                                        <Dropdown.Content className="bg-gray-800 text-gray-100">
                                            <Dropdown.Link to="/login">Iniciar sesión</Dropdown.Link>
                                        </Dropdown.Content>
                                    )}
                                </Dropdown>
                            </div>

                            <div className="-me-2 flex items-center sm:hidden">
                                <button
                                    onClick={() =>
                                        setShowingNavigationDropdown(
                                            (previousState) => !previousState,
                                        )
                                    }
                                    className="inline-flex items-center justify-center rounded-md p-2 text-gray-200 hover:bg-gray-800 focus:bg-gray-800 focus:outline-none"
                                >
                                    <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                                        <path className={!showingNavigationDropdown ? 'inline-flex' : 'hidden'} strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                                        <path className={showingNavigationDropdown ? 'inline-flex' : 'hidden'} strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                    <div className={(showingNavigationDropdown ? 'block' : 'hidden') + ' sm:hidden bg-gray-800'}>
                    <div className="space-y-1 pb-3 pt-2 px-4">
                        {/* Enlaces del menú móvil (se puede ampliar si se desea) */}
                    </div>

                    <div className="border-t border-gray-700 pb-1 pt-4 px-4">
                        <div>
                            <div className="text-base font-medium text-gray-100">{user?.name ?? 'Invitado'}</div>
                            <div className="text-sm font-medium text-gray-400">{user?.email ?? ''}</div>
                        </div>

                        <div className="mt-3 space-y-1">
                            <ResponsiveNavLink to="/profile" className="text-gray-100">Perfil</ResponsiveNavLink>
                            <ResponsiveNavLink as="button" onClick={logout} className="text-gray-100">Cerrar sesión</ResponsiveNavLink>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Header principal eliminado: ahora se utiliza la barra superior con logo y avatar */}

            <main className="flex-1 overflow-auto">{children}</main>
        </div>
    );
}
