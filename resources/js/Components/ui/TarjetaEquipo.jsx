import { ChevronRight } from "lucide-react";

export default function TarjetaEquipo({ equipo }) {
  return (
    <div className={`${equipo.color} rounded-xl p-6 flex items-center justify-between hover:opacity-90 transition-opacity`}>
      <div>
        <h3 className="text-xl font-bold mb-2">{equipo.nombre}</h3>
        <button className="text-white hover:bg-white/20 flex items-center">
          VER EQUIPO <ChevronRight className="h-4 w-4 ml-2" />
        </button>
      </div>
      <img
        src={equipo.logo || "/placeholder.svg"}
        alt={equipo.nombre}
        className="h-12 w-auto object-contain"
      />
    </div>
  );
}
