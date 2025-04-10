import { useState } from "react";
import { ChevronRight } from "lucide-react";
import axios from "axios";
import { Modal, Button } from "react-bootstrap";

export default function TarjetaNoticia({ articulo }) {
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState("Cargando contenido...");
  const [error, setError] = useState(null);

  // Formatear la fecha para mostrarla en formato DD-MM-YYYY
  const fechaFormateada = articulo.publishedAt
    ? (() => {
        const [year, month, day] = articulo.publishedAt.split("T")[0].split("-");
        return `${day}-${month}-${year}`;
      })()
    : "Fecha no disponible";

  // Limpiar el contenido para eliminar "[+2804 chars]" si aparece
  const contenidoLimpio = articulo.content
    ? articulo.content.replace(/\[\+\d+\schars\]/, "").trim()
    : "Contenido no disponible";

  // Función para redirigir a la URL de la noticia
  const handleLeerMas = () => {
    window.open(articulo.url, "_blank"); // Abrir una pestaña con la noticia
  };

  return (
    <div className="bg-gray-800 border border-gray-700 overflow-hidden hover:border-red-600 transition-colors rounded-lg relative">
      {/* Tamaño fijo para la imagen */}
      <div className="relative" style={{ height: "300px", width: "100%" }}>
        <img
          src={articulo.urlToImage || "/placeholder.svg"}
          alt={articulo.title}
          className="w-full h-full object-cover"
          style={{ objectPosition: "top" }}
        />
      </div>
      <div className="p-6">
        <div className="text-sm text-gray-400 mb-2">{fechaFormateada}</div>
        <h3 className="text-xl font-bold mb-2">{articulo.title}</h3>
        <p className="text-gray-300 mb-4">{contenidoLimpio}</p>
      </div>
      {/* Botón posicionado abajo a la izquierda de toda la tarjeta */}
      <button
        onClick={handleLeerMas}
        className="text-red-500 hover:text-red-400 flex items-center absolute bottom-4 left-4"
      >
        LEER MÁS <ChevronRight className="h-4 w-4 ml-1" />
      </button>
    </div>
  );
}
