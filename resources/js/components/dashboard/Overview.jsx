export default function Overview() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Central area: car sketch + tech development panel */}
            <div className="lg:col-span-2 space-y-6">
                <div className="bg-gray-800 rounded-lg p-6 shadow">
                    <div className="flex flex-col lg:flex-row items-start gap-6">
                        {/* Car sketch */}
                        <div className="flex-1 flex items-center justify-center bg-gray-900 rounded-md p-6">
                            <svg
                                className="w-full h-56 max-h-56"
                                viewBox="0 0 800 300"
                                xmlns="http://www.w3.org/2000/svg"
                                preserveAspectRatio="xMidYMid meet"
                            >
                                <g fill="none" stroke="#f3f4f6" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                                    {/* Main silhouette */}
                                    <path d="M60 200 C120 140, 220 120, 340 130 C420 135, 520 150, 640 140 C700 135, 740 120, 760 100" />
                                    {/* Body */}
                                    <path d="M140 200 L180 170 L260 160 L360 165 L440 170 L540 170 L600 200" />
                                    {/* Nose */}
                                    <path d="M60 200 L140 200" />
                                    <path d="M600 200 L720 200" />
                                    {/* Wheels */}
                                    <circle cx="200" cy="220" r="28" />
                                    <circle cx="200" cy="220" r="12" />
                                    <circle cx="560" cy="220" r="28" />
                                    <circle cx="560" cy="220" r="12" />
                                    {/* Cockpit / airbox */}
                                    <path d="M300 160 L340 130 L460 130 L500 160" />
                                    {/* Front wing */}
                                    <path d="M60 200 L20 210 L80 210" />
                                    {/* Rear wing */}
                                    <path d="M700 135 L740 115 L760 115" />
                                    <path d="M740 115 L740 145" />
                                </g>
                            </svg>
                        </div>

                        {/* Tech Development panel */}
                        <aside className="w-full lg:w-72 bg-gray-900 rounded-md p-4">
                            <h3 className="text-sm font-semibold text-gray-200 mb-4 uppercase tracking-wide">
                                Tech Development
                            </h3>
                            <div className="space-y-4">
                                {[
                                    { key: 'chassis',      label: 'Chassis',       level: 1 },
                                    { key: 'engine',       label: 'Engine',        level: 1 },
                                    { key: 'aerodynamics', label: 'Aerodynamics',  level: 2 },
                                    { key: 'suspension',   label: 'Suspension',    level: 3 },
                                    { key: 'electronics',  label: 'Electronics',   level: 4 },
                                ].map(({ key, label, level }) => {
                                    const color =
                                        level >= 5 ? 'bg-green-500'  :
                                        level >= 4 ? 'bg-lime-500'   :
                                        level >= 3 ? 'bg-yellow-500' :
                                        level >= 2 ? 'bg-orange-500' :
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

                {/* Bottom statistics */}
                <div className="bg-gray-800 rounded-lg p-4 shadow">
                    <h4 className="text-sm font-semibold text-gray-200 mb-4 uppercase tracking-wide">Statistics</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-center">
                        {[
                            { value: 4,  label: 'Wins'         },
                            { value: 9,  label: 'Podiums'      },
                            { value: 14, label: 'Races'        },
                            { value: 33, label: 'Fastest laps' },
                            { value: 2,  label: 'DNFs'         },
                        ].map(({ value, label }) => (
                            <div key={label} className="bg-gray-900 rounded-md py-3 px-2">
                                <div className="text-2xl font-bold text-white">{value}</div>
                                <div className="text-xs text-gray-400 mt-1">{label}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Right sidebar: season metrics */}
            <aside className="bg-gray-800 rounded-lg p-4 shadow space-y-4">
                <h3 className="text-sm font-semibold text-gray-200 uppercase tracking-wide">Season Metrics</h3>
                <div className="divide-y divide-gray-700">
                    {[
                        { label: 'Points',  value: 120,      color: 'text-yellow-400' },
                        { label: 'Credits', value: '12,000', color: 'text-green-400'  },
                        { label: 'Wins',    value: 3,        color: 'text-red-400'    },
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
