"use client"

import { useState } from "react"
import ClasificacionPilotos from "../ui/calificacion-pilotos"

export default function SeccionClasificaciones() {
  const [pestanaActiva, setPestanaActiva] = useState("pilotos")

  return (
    <section id="clasificaciones" className="py-16 bg-black">
      <div className="container mx-auto px-4">
        <h2 className="text-3xl font-bold mb-10">CLASIFICACIONES ACTUALES</h2>

        <div className="w-full">
          <div className="flex border-b border-gray-700 mb-8">
            <button
              className={`px-6 py-3 font-medium ${pestanaActiva === "pilotos" ? "text-white bg-red-600 rounded-t-lg" : "text-gray-400 hover:text-white"}`}
              onClick={() => setPestanaActiva("pilotos")}
            >
              PILOTOS
            </button>
          </div>

          <div>
            {pestanaActiva === "pilotos" && <ClasificacionPilotos />}
          </div>
        </div>
      </div>
    </section>
  )
}

