import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Html } from '@react-three/drei';

function CarModel({ src }) {
    const gltf = useGLTF(src);
    return <primitive object={gltf.scene} dispose={null} />;
}

export default function Overview() {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Central area: car sketch + tech development panel */}
            <div className="lg:col-span-2 space-y-6">
                <div className="bg-gray-800 rounded-lg p-6 shadow">
                    <div className="flex flex-col lg:flex-row items-start gap-6">
                        {/* Car sketch: reemplazado por visor 3D (glTF/GLB) */}
                        <div className="flex-1 flex items-center justify-center bg-gray-900 rounded-md p-6">
                            <div className="w-full h-56 max-h-56">
                                <Canvas style={{ width: '100%', height: '100%' }} camera={{ position: [0, 0, 6], fov: 45 }}>
                                    <ambientLight intensity={0.6} />
                                    <directionalLight position={[10, 10, 5]} intensity={0.8} />
                                    <Suspense fallback={<Html center><div className="text-gray-300 text-sm">Cargando 3D…</div></Html>}>
                                        <CarModel src="/models/car.glb" />
                                    </Suspense>
                                    <OrbitControls enablePan enableZoom enableRotate />
                                </Canvas>
                            </div>
                        </div>

                        {/* Panel de Desarrollo Tecnológico */}
                        <aside className="w-full lg:w-72 bg-gray-900 rounded-md p-4">
                            <h3 className="text-sm font-semibold text-gray-200 mb-4 uppercase tracking-wide">
                                Desarrollo Tecnológico
                            </h3>
                            <div className="space-y-4">
                                {[
                                    { key: 'chassis',      label: 'Chasis',        level: 1 },
                                    { key: 'engine',       label: 'Motor',         level: 1 },
                                    { key: 'aerodynamics', label: 'Aerodinámica',  level: 2 },
                                    { key: 'suspension',   label: 'Suspensión',    level: 3 },
                                    { key: 'electronics',  label: 'Electrónica',   level: 4 },
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

                {/* Estadísticas inferiores */}
                <div className="bg-gray-800 rounded-lg p-4 shadow">
                    <h4 className="text-sm font-semibold text-gray-200 mb-4 uppercase tracking-wide">Estadísticas</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-center">
                        {[
                            { value: 4,  label: 'Victorias'       },
                            { value: 9,  label: 'Podios'          },
                            { value: 14, label: 'Carreras'        },
                            { value: 33, label: 'Vueltas rápidas' },
                            { value: 2,  label: 'DNFs'            },
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
                        { label: 'Puntos',   value: 120,      color: 'text-yellow-400' },
                        { label: 'Créditos', value: '12.000', color: 'text-green-400'  },
                        { label: 'Victorias', value: 3,       color: 'text-red-400'    },
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
