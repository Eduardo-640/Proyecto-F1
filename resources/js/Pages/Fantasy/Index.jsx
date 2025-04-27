import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Navbar from '@/Components/cabeceras/Navbar';
import Compra from './Compra';
import Venta from './Venta';
import MiEquipo from './MiEquipo';
import Equipos from './Equipos';

const FantasyIndex = () => {
    const [pestanaActiva, setPestanaActiva] = useState('equipos');
    const [presupuesto, setPresupuesto] = useState(0);

    useEffect(() => {
        const fetchPresupuesto = async () => {
            try {
                const response = await axios.get('/api/usuario/presupuesto');
                setPresupuesto(response.data.presupuesto);
            } catch (error) {
                console.error('Error al obtener el presupuesto:', error);
            }
        };

        fetchPresupuesto();
    }, []);

    const actualizarPresupuesto = (nuevoPresupuesto) => {
        setPresupuesto(nuevoPresupuesto);
    };

    return (
        <>
            <Navbar />
            <div className="container">
                <h1>Bienvenido a Manager F1</h1>
                <p>¡Crea tu equipo, selecciona tus pilotos favoritos y compite con otros usuarios!</p>

                <div className="w-full flex justify-between items-center border-b border-gray-700 mb-8">
                    <div className="flex">
                        <button
                            className={`px-6 py-3 font-medium ${pestanaActiva === 'equipos' ? 'text-white bg-red-600 rounded-t-lg' : 'text-gray-400 hover:text-white'}`}
                            onClick={() => setPestanaActiva('equipos')}
                        >
                            EQUIPOS
                        </button>
                        <button
                            className={`px-6 py-3 font-medium ${pestanaActiva === 'mi-equipo' ? 'text-white bg-red-600 rounded-t-lg' : 'text-gray-400 hover:text-white'}`}
                            onClick={() => setPestanaActiva('mi-equipo')}
                        >
                            MI EQUIPO
                        </button>
                        <button
                            className={`px-6 py-3 font-medium ${pestanaActiva === 'compra' ? 'text-white bg-red-600 rounded-t-lg' : 'text-gray-400 hover:text-white'}`}
                            onClick={() => setPestanaActiva('compra')}
                        >
                            COMPRA
                        </button>
                        <button
                            className={`px-6 py-3 font-medium ${pestanaActiva === 'venta' ? 'text-white bg-red-600 rounded-t-lg' : 'text-gray-400 hover:text-white'}`}
                            onClick={() => setPestanaActiva('venta')}
                        >
                            VENTA
                        </button>
                    </div>
                    <div className="text-white font-bold">Presupuesto: ${presupuesto}</div>
                </div>

                <div>
                    {pestanaActiva === 'equipos' && <Equipos actualizarPresupuesto={actualizarPresupuesto} />}
                    {pestanaActiva === 'mi-equipo' && <MiEquipo actualizarPresupuesto={actualizarPresupuesto} />}
                    {pestanaActiva === 'compra' && <Compra actualizarPresupuesto={actualizarPresupuesto} />}
                    {pestanaActiva === 'venta' && <Venta actualizarPresupuesto={actualizarPresupuesto} />}
                </div>
            </div>
        </>
    );
};

export default FantasyIndex;