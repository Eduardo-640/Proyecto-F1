import { useState, useEffect } from "react";
import axios from "axios";
import TarjetaNoticia from "../ui/TarjetaNoticia";

export default function SeccionUltimasNoticias() {
  const [noticias, setNoticias] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios
      .get("/api/noticias")
      .then((response) => {
        setNoticias(response.data.articles || []); // Ajusta según la estructura del JSON
      })
      .catch((error) => {
        console.error("Error al obtener las noticias:", error);
        setError("No se pudieron cargar las noticias.");
      });
  }, []);

  return (
    <section id="noticias" className="py-16 bg-gradient-to-b from-black to-gray-900">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-3xl font-bold">ÚLTIMAS NOTICIAS</h2>
          <a
            href="/noticias" // Cambia esta ruta según la configuración de tu aplicación
            className="border border-red-600 text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded-md font_enlaces"
          >
            VER TODAS LAS NOTICIAS
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {noticias.slice(0, 3).map((articulo, index) => (
            <TarjetaNoticia key={index} articulo={articulo} />
          ))}
        </div>
      </div>
    </section>
  );
}

