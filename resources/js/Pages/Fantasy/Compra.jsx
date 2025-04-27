import axios from 'axios';
import React, { useState, useEffect } from 'react';

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
            const response = await axios.post('/fantasy/comprar-piloto', { piloto_id: pilotoId });
            setFlashMessage({ message: response.data.message, isError: false }); 

            // Actualizar la lista de pilotos después de la compra
            setPilotos((prevPilotos) => prevPilotos.filter((piloto) => piloto.id !== pilotoId));

            // Actualizar el presupuesto dinámicamente
            const presupuestoResponse = await axios.get('/api/usuario/presupuesto');
            actualizarPresupuesto(presupuestoResponse.data.presupuesto);
        } catch (error) {
            console.error('Error al comprar piloto:', error);
            setFlashMessage({ message: 'No se pudo comprar el piloto.', isError: true });
        }
    };

    useEffect(() => {
        // Obtener pilotos desde el backend
        const fetchPilotos = async () => {
            try {
                const response = await axios.get('/fantasy/pilotos');
                setPilotos(response.data);
            } catch (error) {
                console.error('Error al obtener pilotos:', error);
            }
        };

        fetchPilotos();
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