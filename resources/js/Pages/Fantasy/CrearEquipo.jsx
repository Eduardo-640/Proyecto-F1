import axios from 'axios';
import React, { useState, useEffect } from 'react';

const CrearEquipo = () => {
    const [nombre, setNombre] = useState('');
    const presupuesto = 100000000; // Presupuesto inicial fijo
    const [escuderias, setEscuderias] = useState([]);
    // const [pilotos, setPilotos] = useState([]);
    // const [pilotosSeleccionados, setPilotosSeleccionados] = useState([]);
    const [escuderiaSeleccionada, setEscuderiaSeleccionada] = useState('');

    useEffect(() => {
        // Simulación de datos, reemplazar con peticiones reales
        setEscuderias(['Ferrari', 'Mercedes', 'Red Bull', 'McLaren']);
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post('/fantasy/crear', {
                nombre,
                presupuesto,
                escuderia: escuderiaSeleccionada,
            });
            alert('Equipo creado exitosamente');
        } catch (error) {
            console.error('Error al crear el equipo:', error);
            alert('Hubo un error al crear el equipo.');
        }
    };

    return (
        <>
            <div className="container">
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="nombre">Nombre del Equipo</label>
                        <input
                            type="text"
                            id="nombre"
                            className="form-control"
                            value={nombre}
                            onChange={(e) => setNombre(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="escuderia">Escudería</label>
                        <select
                            id="escuderia"
                            className="form-control"
                            value={escuderiaSeleccionada}
                            onChange={(e) => setEscuderiaSeleccionada(e.target.value)}
                            required
                        >
                            <option value="">Selecciona una escudería</option>
                            {escuderias.map((escuderia, index) => (
                                <option key={index} value={escuderia}>
                                    {escuderia}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="form-group">
                        <label htmlFor="presupuesto">Presupuesto</label>
                        <input
                            type="number"
                            id="presupuesto"
                            className="form-control"
                            value={presupuesto}
                            readOnly
                        />
                    </div>

                    <button type="submit" className="btn btn-primary">
                        Crear Equipo
                    </button>
                </form>
            </div>
        </>
    );
};

//export default CrearEquipo;