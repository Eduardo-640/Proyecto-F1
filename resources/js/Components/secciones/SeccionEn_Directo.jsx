

export default function SeccionEn_Directo() {
    return (
        <section className="relative h-[70vh] overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-b from-black/40 to-black z-10"></div>
            <img
                src="/images/imagen_portada_1.jpeg"
                alt="F1 Portada"
                className="absolute inset-0 w-full h-full object-cover"
            />
            <div className="container mx-auto px-4 relative z-20 h-full flex flex-col justify-center">
                <div className="max-w-2xl mt-14">
                    <h1 className="text-4xl md:text-6xl font-bold mb-4">
                        FORMULA 1 <span className="text-red-600">2025</span> SESION
                    </h1>
                    <p className="text-lg md:text-xl mb-8 text-gray-200">
                    Experimente la emoción de la competición de automovilismo más prestigiosa del mundo
                    </p>
                    <div className="flex flex-wrap gap-4">
                    <a href="https://www.dazn.com" target="_blank" rel="noopener noreferrer">
                        <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md">EN DIRECTO</button>
                    </a>
                        <button className="border border-white text-inherit hover:bg-white hover:text-black px-4 py-2 rounded-md">
                            CALENDARIO
                        </button>
                    </div>
                </div>
            </div>
        </section>
    );
}