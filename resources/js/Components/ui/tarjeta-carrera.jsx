import { Calendar, Flag } from "lucide-react";
import  Bandera  from "../ui/bandera-paises";

export default function TarjetaCarrera({ carrera }) {
  return (
    <div className="bg-gray-800 border border-gray-700 hover:border-red-600 transition-colors rounded-lg">
      <div className="p-6">
        <div className="text-2xl mb-2">{Bandera(carrera.bandera)}</div>
        <h3 className="text-xl font-bold mb-2">{carrera.nombre}</h3>
        <div className="flex items-center text-gray-300 mb-1">
          <Calendar className="h-4 w-4 mr-2" />
          <span>{carrera.fecha}</span>
        </div>
        <div className="flex items-center text-gray-300">
          <Flag className="h-4 w-4 mr-2" />
          <span>{carrera.ubicacion}</span>
        </div>
      </div>
    </div>
  )
}

