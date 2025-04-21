"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import TarjetaNoticia from "../Components/ui/TarjetaNoticia";
import Navbar from '@/Components/cabeceras/Navbar';

const Noticias = () => {
    const [noticias, setNoticias] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        axios.get("/api/noticias")
            .then((response) => {
                setNoticias(response.data.articles || []); // Ajusta según la estructura del JSON
            })
            .catch((error) => {
                console.error("Error al obtener las noticias:", error);
                setError("No se pudieron cargar las noticias.");
            });
    }, []);

    return (
        <>
        <Navbar />
        <div className="bg-black text-white p-4">
            <h1 className="text-center">Noticias</h1>
            {error && <p className="text-red-500">{error}</p>}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {noticias.map((noticia, index) => (
                    <TarjetaNoticia key={index} articulo={noticia} />
                ))}
            </div>
        </div>
        </>
    );
};

export default Noticias;