import axios from 'axios';
import React, { useState, useEffect } from 'react';
import { PILOTOS_FANTASY_MOCK, PRESUPUESTO_MOCK } from '../../data/mockData';

const PilotoCard = ({ piloto, onAction, actionLabel }) => {
    return (
        <div className="card" style={{ width: '18rem', margin: '1rem' }}>
            <img src={`/images/imagenes_drivers/${piloto.driver_id}.jpg`}
            onError={(e) => {
                e.target.onerror = null; // Evita un bucle infinito si la imagen de respaldo también falla
                e.target.src = "/images/imagen_respaldo.png"; // Imagen de respaldo
              }}
            className="w-full h-full object-cover"
            style={{ objectPosition: "top" }} 
            alt={piloto.nombre} />

            <div className="card-body">
                <h5 className="card-title">{piloto.nombre}</h5>
                <p className="card-text">Precio: ${piloto.precio.toLocaleString()}</p>
                <button
                    className="btn btn-success"
                    onClick={() => onAction(piloto.id)}
                >
                    {actionLabel}
                </button>
            </div>
        </div>
    );
};

const Compra = ({ actualizarPresupuesto }) => {
    const [pilotos, setPilotos] = useState([]);
    const [flashMessage, setFlashMessage] = useState({ message: null, isError: false }); 

    const handleComprarPiloto = async (pilotoId) => {
        try {
            // TODO: descomentar cuando el backend esté disponible
            // const response = await axios.post('/fantasy/comprar-piloto', { piloto_id: pilotoId });
            // setFlashMessage({ message: response.data.message, isError: false });
            // const presupuestoResponse = await axios.get('/api/usuario/presupuesto');
            // actualizarPresupuesto(presupuestoResponse.data.presupuesto);

            // Simulación mock: eliminar piloto de la lista y mostrar mensaje
            setPilotos((prevPilotos) => prevPilotos.filter((piloto) => piloto.id !== pilotoId));
            setFlashMessage({ message: 'Piloto comprado correctamente (mock).', isError: false });
            actualizarPresupuesto((prev) => prev - 10000000);
        } catch (error) {
            console.error('Error al comprar piloto:', error);
            setFlashMessage({ message: 'No se pudo comprar el piloto.', isError: true });
        }
    };

    useEffect(() => {
        // TODO: descomentar cuando el backend esté disponible
        // const fetchPilotos = async () => {
        //     try {
        //         const response = await axios.get('/fantasy/pilotos');
        //         setPilotos(response.data);
        //     } catch (error) {
        //         console.error('Error al obtener pilotos:', error);
        //     }
        // };
        // fetchPilotos();
        setTimeout(() => {
            setPilotos(PILOTOS_FANTASY_MOCK);
        }, 400);
    }, []);

    return (
        <div className="container bg-gray-900 text-white p-6 rounded-lg shadow-md">
            <h1>Pilotos Disponibles</h1>
            {flashMessage.message && (
                <div className={`text-center py-2 rounded mb-4 ${flashMessage.isError ? 'bg-red-500' : 'bg-green-500'} text-white`}>
                    {flashMessage.message}
                </div>
            )}
            <div className="d-flex flex-wrap">
                {pilotos.map((piloto) => (
                    <PilotoCard
                        key={piloto.id}
                        piloto={piloto}
                        onAction={handleComprarPiloto}
                        actionLabel="Comprar"
                    />
                ))}
            </div>
        </div>
    );
};

export default Compra;