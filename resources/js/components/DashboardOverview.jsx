export default function DashboardOverview() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Área central: boceto del coche + panel de desarrollo */}
            <div className="lg:col-span-2 space-y-6">
                <div className="bg-gray-800 rounded-lg p-6 shadow">
                    <div className="flex flex-col lg:flex-row items-start gap-6">
                        {/* Boceto del coche */}
                        <div className="flex-1 flex items-center justify-center bg-gray-900 rounded-md p-6">
                            <svg
                                className="w-full h-56 max-h-56"
                                viewBox="0 0 800 300"
                                xmlns="http://www.w3.org/2000/svg"
                                preserveAspectRatio="xMidYMid meet"
                            >
                                <g fill="none" stroke="#f3f4f6" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                                    {/* Silueta principal */}
                                    <path d="M60 200 C120 140, 220 120, 340 130 C420 135, 520 150, 640 140 C700 135, 740 120, 760 100" />
                                    {/* Carrocería */}
                                    <path d="M140 200 L180 170 L260 160 L360 165 L440 170 L540 170 L600 200" />
                                    {/* Fondo nariz */}
                                    <path d="M60 200 L140 200" />
                                    <path d="M600 200 L720 200" />
                                    {/* Ruedas */}
                                    <circle cx="200" cy="220" r="28" />
                                    <circle cx="200" cy="220" r="12" />
                                    <circle cx="560" cy="220" r="28" />
                                    <circle cx="560" cy="220" r="12" />
                                    {/* Cockpit / airbox */}
                                    <path d="M300 160 L340 130 L460 130 L500 160" />
                                    {/* Alerón delantero */}
                                    <path d="M60 200 L20 210 L80 210" />
                                    {/* Alerón trasero */}
                                    <path d="M700 135 L740 115 L760 115" />
                                    <path d="M740 115 L740 145" />
                                </g>
                            </svg>
                        </div>

                        {/* Panel de Desarrollo Tecnológico */}
                        <aside className="w-full lg:w-72 bg-gray-900 rounded-md p-4">
                            <h3 className="text-sm font-semibold text-gray-200 mb-4 uppercase tracking-wide">
                                Desarrollo Tecnológico
                            </h3>
                            <div className="space-y-4">
                                {[
                                    { key: 'chassis',      label: 'Chasis',       level: 1 },
                                    { key: 'engine',       label: 'Motor',        level: 1 },
                                    { key: 'aerodynamics', label: 'Aerodinámica', level: 2 },
                                    { key: 'suspension',   label: 'Suspensión',   level: 3 },
                                    { key: 'electronics',  label: 'Electrónica',  level: 4 },
                                ].map(({ key, label, level }) => {
                                    const color =
                                        level >= 5 ? 'bg-green-500' :
                                        level >= 4 ? 'bg-lime-500'  :
                                        level >= 3 ? 'bg-yellow-500':
                                        level >= 2 ? 'bg-orange-500':
                                                     'bg-red-500';
                                    return (
                                        <div key={key}>
                                            <div className="flex justify-between text-xs text-gray-400 mb-2">
                                                <span>{label}</span>
                                                <span className="font-medium text-gray-300">{level} / 5</span>
                                            </div>
                                            <div className="flex gap-1">
                                                {Array.from({ length: 5 }, (_, i) => (
                                                    <div
                                                        key={i}
                                                        className={`flex-1 h-2 rounded-sm ${i < level ? color : 'bg-gray-700'}`}
                                                    />
                                                ))}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </aside>
                    </div>
                </div>

                {/* Estadísticas inferiores */}
                <div className="bg-gray-800 rounded-lg p-4 shadow">
                    <h4 className="text-sm font-semibold text-gray-200 mb-4 uppercase tracking-wide">Estadísticas</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-center">
                        {[
                            { value: 4,  label: 'Victorias' },
                            { value: 9,  label: 'Podios' },
                            { value: 14, label: 'Carreras' },
                            { value: 33, label: 'Vueltas rápidas' },
                            { value: 2,  label: 'DNFs' },
                        ].map(({ value, label }) => (
                            <div key={label} className="bg-gray-900 rounded-md py-3 px-2">
                                <div className="text-2xl font-bold text-white">{value}</div>
                                <div className="text-xs text-gray-400 mt-1">{label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Sidebar derecho: métricas de temporada */}
            <aside className="bg-gray-800 rounded-lg p-4 shadow space-y-4">
                <h3 className="text-sm font-semibold text-gray-200 uppercase tracking-wide">Métricas de Temporada</h3>
                <div className="divide-y divide-gray-700">
                    {[
                        { label: 'Puntos',   value: 120,     color: 'text-yellow-400' },
                        { label: 'Créditos', value: '12.000', color: 'text-green-400' },
                        { label: 'Victorias', value: 3,      color: 'text-red-400' },
                    ].map(({ label, value, color }) => (
                        <div key={label} className="flex items-center justify-between py-3">
                            <span className="text-sm text-gray-400">{label}</span>
                            <span className={`text-xl font-bold ${color}`}>{value}</span>
                        </div>
                    ))}
                </div>
            </aside>
        </div>
    );
}
