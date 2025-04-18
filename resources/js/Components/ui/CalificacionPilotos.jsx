import { useEffect, useState } from "react";

export default function ClasificacionPilotos() {
    const [pilotos, setPilotos] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Realizar la solicitud a la API
        const fetchCalificaciones = async () => {
            try {
                const response = await fetch("/api/calificacionesActuales");
                                
                if (!response.ok) {
                    throw new Error("Error al obtener las calificaciones");
                }
                const data = await response.json();
                console.log("Datos de la API:", data); // Verifica qué datos llegan
                setPilotos(data);
            } catch (error) {
                console.error("Error al cargar las calificaciones:", error);
                setError("No se pudieron cargar las calificaciones.");
            }
        };

        fetchCalificaciones();
    }, []);

    return (
        <div className="bg-gray-800 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="bg-gray-900">
                            <th className="py-4 px-6 text-left">POS</th>
                            <th className="py-4 px-6 text-left">PILOTO</th>
                            <th className="py-4 px-6 text-left">NACIONALIDAD</th>
                            <th className="py-4 px-6 text-left">EQUIPO</th>
                            <th className="py-4 px-6 text-right">PUNTOS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {error ? (
                            <tr>
                                <td colSpan="5" className="py-4 px-6 text-center text-red-500">
                                    {error}
                                </td>
                            </tr>
                        ) : (
                            pilotos.map((piloto, index) => (
                                <tr key={index} className="border-t border-gray-700 hover:bg-gray-700">
                                    <td className="py-4 px-6">{index + 1}</td>
                                    <td className="py-4 px-6 font-medium">{piloto.Driver.givenName} {piloto.Driver.familyName}</td>
                                    <td className="py-4 px-6">{piloto.Driver.nationality}</td>
                                    <td className="py-4 px-6">{piloto.Constructors[0].name || "Desconocido"}</td>
                                    <td className="py-4 px-6 text-right font-bold">{piloto.points}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

