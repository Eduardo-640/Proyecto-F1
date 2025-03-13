import { Link } from "@inertiajs/react";

export default function PiePagina() {
    return (
        <footer className="bg-black py-12 border-t border-gray-800">
            <div className="container mx-auto px-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div>
                        <Link href="/" className="flex items-center mb-6 font_enlaces">
                            <img src="/favicon-32x32.png" alt="Icono F1" />
                            <span className="text-xl text-white font-semibold">FÓRMULA 1</span>
                        </Link>
                        <p className="text-gray-400 mb-6">El hogar oficial de las carreras de Fórmula 1.</p>
                        <div className="flex space-x-4">
                            <IconoSocial nombre="Facebook" icono="facebook" />
                            <IconoSocial nombre="Instagram" icono="instagram" />
                            <IconoSocial nombre="Twitter" icono="twitter" />
                            <IconoSocial nombre="YouTube" icono="youtube" />
                        </div>
                    </div>

                    <EnlacesPiePagina
                        titulo="ACERCA DE"
                        enlaces={[
                            { etiqueta: "Acerca de Fórmula 1", href: "#" },
                            { etiqueta: "Historia", href: "#" },
                            { etiqueta: "Socios de F1", href: "#" },
                            { etiqueta: "Sostenibilidad", href: "#" },
                        ]}
                    />

                    <EnlacesPiePagina
                        titulo="CAMPEONATO"
                        enlaces={[
                            { etiqueta: "Clasificación de Pilotos", href: "#" },
                            { etiqueta: "Clasificación de Constructores", href: "#" },
                            { etiqueta: "Archivo", href: "#" },
                            { etiqueta: "Premios F1", href: "#" },
                        ]}
                    />

                    <EnlacesPiePagina
                        titulo="EXPLORAR"
                        enlaces={[
                            { etiqueta: "F1 TV", href: "#" },
                            { etiqueta: "Tienda F1", href: "#" },
                            { etiqueta: "Experiencias F1", href: "#" },
                            { etiqueta: "F1 Auténticos", href: "#" },
                        ]}
                    />
                </div>

                <div className="mt-12 pt-8 border-t border-gray-800 text-center text-gray-500 text-sm">
                    <p>© 2025 Formula One World Championship Limited</p>
                </div>
            </div>
        </footer>
    )
}

function EnlacesPiePagina({ titulo, enlaces }) {
    return (
        <div>
            <h3 className="text-lg font-semibold mb-4">{titulo}</h3>
            <ul className="space-y-3">
                {enlaces.map((enlace, index) => (
                    <li key={index}>
                        <Link href={enlace.href} className="text-gray-400 hover:text-white">
                            {enlace.etiqueta}
                        </Link>
                    </li>
                ))}
            </ul>
        </div>
    )
}

function IconoSocial({ nombre, icono }) {
    return (
        <a href="#" className="text-gray-400 hover:text-white text-xl">
            <i className={`bi bi-${icono}`}></i>
            <span className="sr-only">{nombre}</span>
        </a>
    )
}

