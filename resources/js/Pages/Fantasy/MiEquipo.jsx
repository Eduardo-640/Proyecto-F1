import axios from 'axios';
import React, { useState, useEffect } from 'react';

const PilotoCard = ({ piloto, onAction, actionLabel, seleccionado }) => {
    return (
        <div className={`card ${seleccionado ? 'border-success' : ''}`} style={{ width: '18rem', margin: '1rem' }}>
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
                <div className="form-check">
                    <input
                        type="checkbox"
                        className="form-check-input"
                        checked={seleccionado}
                        onChange={(e) => onAction(piloto.id, e.target.checked)}
                    />
                    <label className="form-check-label ml-2">Seleccionar para jugar</label>
                </div>
            </div>
        </div>
    );
};

const MiEquipo = () => {
    const [pilotos, setPilotos] = useState([]);
    const [flashMessage, setFlashMessage] = useState({ message: null, isError: false }); 

    const handleSeleccionarPiloto = async (pilotoId, seleccionado) => {
        try {
            const seleccionados = pilotos.filter((piloto) => piloto.pivot.seleccionado).length;
            if (seleccionado && seleccionados >= 2) {
                setFlashMessage({ message: 'Solo puedes seleccionar un máximo de dos pilotos para jugar.', isError: true });
                return;
            }

            const response = await axios.post('/fantasy/seleccionar-piloto', {
                piloto_id: pilotoId,
                seleccionado,
            });
            setFlashMessage({ message: response.data.message, isError: false }); 

            setPilotos((prevPilotos) =>
                prevPilotos.map((piloto) =>
                    piloto.id === pilotoId ? { ...piloto, pivot: { ...piloto.pivot, seleccionado } } : piloto
                )
            );
        } catch (error) {
            console.error('Error al seleccionar piloto:', error);
            setFlashMessage({ message: 'No se pudo actualizar el estado de selección.', isError: true });
        }
    };

    useEffect(() => {
        const fetchPilotos = async () => {
            try {
                const response = await axios.get('/fantasy/mi-equipo');
                setPilotos(response.data);
            } catch (error) {
                console.error('Error al obtener pilotos:', error);
            }
        };

        fetchPilotos();
    }, []);

    return (
        <div className="container bg-gray-900 text-white p-6 rounded-lg shadow-md">
            <h1 className="text-center mb-4">Mi Equipo</h1>
            {flashMessage.message && (
                <div className={`text-center py-2 rounded mb-4 ${flashMessage.isError ? 'bg-red-500' : 'bg-green-500'} text-white`}>
                    {flashMessage.message}
                </div>
            )}
            <div className="d-flex flex-wrap justify-content-center">
                {pilotos.map((piloto) => (
                    <PilotoCard
                        key={piloto.id}
                        piloto={piloto}
                        onAction={handleSeleccionarPiloto}
                        actionLabel="Seleccionar"
                        seleccionado={piloto.pivot.seleccionado}
                    />
                ))}
            </div>
        </div>
    );
};

export default MiEquipo;