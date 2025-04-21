"use client"

import { useState, useEffect } from "react"
import axios from "axios"
import TarjetaPiloto from "../Components/ui/TarjetaPiloto";
import Navbar from "@/Components/cabeceras/Navbar";

export default function Pilotos() {
    const [year, setYear] = useState(new Date().getFullYear())
    const [pilotos, setPilotos] = useState([])
    const [loading, setLoading] = useState(true)
    const years = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - i)

    useEffect(() => {
        const fetchPilotos = async () => {
            setLoading(true)
            try {
                // Simulamos una carga de datos
                await new Promise((resolve) => setTimeout(resolve, 800))

                const response = await axios.get(`/api/pilotos/${year}`);
                console.log("Respuesta de la API:", response.data); // Verifica qué datos llegan
                const pilotosData = response.data; 
                setPilotos(pilotosData)
            } catch (error) {
                console.error("Error al obtener los pilotos:", error)
                setPilotos([]) 
            } finally {
                setLoading(false)
            }
        }

        fetchPilotos()
    }, [year])


    return (
        <>
        <Navbar />
        <div className="container py-8">
            <h1 className="text-center">Pilotos F1 {year}</h1>

            {/* Selector de año */}
            <div className="text-center my-3">
                <label className="me-2 fs-4 fw-bold">Selecciona un año:</label>
                <select
                    className="form-select form-select-lg d-inline-block w-auto text-white bg-dark"
                    value={year}
                    onChange={(e) => setYear(e.target.value)}
                >
                    {years.map((y) => (
                        <option key={y} value={y}>
                            {y}
                        </option>
                    ))}
                </select>
            </div>

            {/* Mostrar mensaje de carga */}
            {loading && (
                <div className="flex justify-center items-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-600 mr-3"></div>
                    <p className="text-white font-medium">Cargando pilotos...</p>
                </div>
            )}

            {/* Mensaje si no hay pilotos */}
            {!loading && pilotos.length === 0 && (
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center my-8">
                    <i className="bi bi-exclamation-triangle-fill text-yellow-500 text-3xl mb-3"></i>
                    <p className="text-white text-lg">No hay pilotos disponibles para la temporada {year}.</p>
                </div>
            )}

            {/* Grid de pilotos */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pilotos.map((piloto, index) => (
                    <TarjetaPiloto key={index} piloto={piloto} year={year} />
                ))}
            </div>
        </div>
        </>
    )
}