
export default function GuestLayout({ children }) {
    return (
        <div className="flex min-h-screen flex-col items-center bg-gray-900 pt-6 sm:justify-center sm:pt-0">
            <div>
                <img src="/icono F1.png" alt="Logo del Proyecto" className="h-32 w-32" />
            </div>

            <div className="mt-6 w-full max-w-md overflow-hidden rounded-lg bg-gray-800 px-6 py-4 shadow-lg">
                {children}
            </div>
        </div>
    );
}
