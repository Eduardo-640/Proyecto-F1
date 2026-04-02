"use client";

import { useState, useEffect } from "react";
import NewsCard from '@/components/ui/NewsCard';
import Navbar from '@/components/Navbar';
import { NOTICIAS_MOCK } from '@/data/mockData';

const Noticias = () => {
    const [noticias, setNoticias] = useState([]);

    useEffect(() => {
        // TODO: reemplazar con axios.get("/api/noticias") cuando el backend esté disponible
        setNoticias(NOTICIAS_MOCK);
    }, []);

    return (
        <>
            <Navbar />
            <div className="bg-black text-white p-4">
                <h1 className="text-center mb-8">Noticias</h1>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {noticias.map((noticia, index) => (
                        <NewsCard key={index} articulo={noticia} />
                    ))}
                </div>
            </div>
        </>
    );
};

export default Noticias;
