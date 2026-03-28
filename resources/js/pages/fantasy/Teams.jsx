import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FANTASY_EQUIPOS_MOCK } from '../../data/mockData';

const EquipoCard = ({ usuario }) => {
    return (
        <div className="card shadow-lg" style={{ width: '20rem', margin: '1rem' }}>
            <div className="card-body">
                <h5 className="card-title text-center font-bold text-lg">{usuario.name}</h5>
                <p className="card-text text-center text-gray-500">Puntos: {usuario.puntos}</p>
                <h6 className="text-center font-semibold mt-3">Pilotos Seleccionados:</h6>
                <ul className="list-disc list-inside">
                    {usuario.pilotos.map((piloto) => (
                        <li key={piloto.id} className="text-gray-700">{piloto.nombre}</li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

const Equipos = () => {
    const [usuarios, setUsuarios] = useState([]);

    useEffect(() => {
        // TODO: descomentar cuando el backend esté disponible
        // const fetchUsuarios = async () => {
        //     try {
        //         const response = await axios.get('/fantasy/equipos');
        //         const usuariosOrdenados = response.data.sort((a, b) => b.puntos - a.puntos);
        //         setUsuarios(usuariosOrdenados);
        //     } catch (error) {
        //         console.error('Error al obtener los equipos:', error);
        //     }
        // };
        // fetchUsuarios();
        setTimeout(() => {
            setUsuarios([...FANTASY_EQUIPOS_MOCK].sort((a, b) => b.puntos - a.puntos));
        }, 400);
    }, []);

    return (
        <div className="container bg-gray-900 text-white p-6 rounded-lg shadow-md">
            <h1 className="text-center text-3xl font-bold mb-6">Equipos y Pilotos Seleccionados</h1>
            <div className="d-flex flex-wrap justify-content-center">
                {usuarios.map((usuario) => (
                    <EquipoCard key={usuario.id} usuario={usuario} />
                ))}
            </div>
        </div>
    );
};

export default Equipos;