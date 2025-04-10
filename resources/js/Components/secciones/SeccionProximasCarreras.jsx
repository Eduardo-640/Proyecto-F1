import { useState, useEffect } from "react";
import { Calendar, ChevronRight, Clock } from "lucide-react";
import axios from "axios";
import { format } from "date-fns"; // Importar función de formateo
import es from "date-fns/locale/es"; // Importar el idioma español

export default function SeccionProximasCarreras() {
    const [proximaCarrera, setProximaCarrera] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Realizar la petición a la API
        const fetchProximaCarrera = async () => {
            try {
                const response = await axios.get("/api/proximaCarrera");
                setProximaCarrera(response.data);
            } catch (err) {
                setError("No se pudo cargar la próxima carrera.");
            } finally {
                setLoading(false);
            }
        };

        fetchProximaCarrera();
    }, []);

    // Función para formatear la hora
    const formatearHora = (hora) => {
        if (!hora) return "Hora no disponible";
        try {
            const [hours, minutes] = hora.split(":");
            const date = new Date();
            date.setHours(hours, minutes);
            return format(date, "hh:mm a", { locale: es }); // Formato 12 horas con AM/PM
        } catch {
            return "Hora no disponible";
        }
    };

    if (loading) {
        return (
            <div className="text-center py-5">
                <div className="spinner-border text-danger" role="status">
                    <span className="visually-hidden">Cargando...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="text-center py-5">
                <p className="text-red-500">{error}</p>
            </div>
        );
    }

    return (
        <div className="container mx-auto px-4 z-30">
            <div className="flex flex-col md:flex-row items-center justify-between bg-gray-800 rounded-xl p-6 md:p-8">
                <div>
                    <div className="text-red-500 font-medium mb-2">PRÓXIMA CARRERA</div>
                    <h2 className="text-2xl md:text-3xl font-bold mb-2">
                        {proximaCarrera.raceName || "Carrera no disponible"}
                    </h2>
                    <div className="flex items-center gap-4 text-gray-300">
                        <div className="flex items-center">
                            <Calendar className="h-4 w-4 mr-2" />
                            <span>{proximaCarrera.date || "Fecha no disponible"}</span>
                        </div>
                        <div className="flex items-center">
                            <Clock className="h-4 w-4 mr-2" />
                            <span>{formatearHora(proximaCarrera.time)}</span>
                        </div>
                    </div>
                </div>
                <div className="mt-6 md:mt-0">
                    <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md flex items-center">
                        MÁS DETALLES <ChevronRight className="h-4 w-4 ml-2" />
                    </button>
                </div>
            </div>
        </div>
    );
}