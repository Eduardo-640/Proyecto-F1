import { ChevronRight } from "lucide-react";

export default function TarjetaNoticia({ articulo }) {
  return (
    <div className="bg-gray-800 border border-gray-700 overflow-hidden hover:border-red-600 transition-colors rounded-lg">
      <div className="relative h-48">
        <img
          src={articulo.img || "/placeholder.svg"}
          alt={articulo.titulo}
          className="w-full h-full object-cover"
        />
      </div>
      <div className="p-6">
        <div className="text-sm text-gray-400 mb-2">{articulo.fecha}</div>
        <h3 className="text-xl font-bold mb-2">{articulo.titulo}</h3>
        <p className="text-gray-300 mb-4">{articulo.extracto}</p>
        <button className="text-red-500 hover:text-red-400 flex items-center">
          LEER MÁS <ChevronRight className="h-4 w-4 ml-1" />
        </button>
      </div>
    </div>
  );
}
