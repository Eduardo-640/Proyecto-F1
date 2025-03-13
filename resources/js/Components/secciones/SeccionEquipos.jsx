import TarjetaEquipo from "../ui/tarjeta-equipo"

export default function SeccionEquipos() {
  const equipos = [
    { nombre: "Red Bull Racing", logo: "/placeholder.svg?height=100&width=200", color: "bg-blue-900" },
    { nombre: "Ferrari", logo: "/placeholder.svg?height=100&width=200", color: "bg-red-700" },
    { nombre: "Mercedes", logo: "/placeholder.svg?height=100&width=200", color: "bg-teal-800" },
    { nombre: "McLaren", logo: "/placeholder.svg?height=100&width=200", color: "bg-orange-700" },
    { nombre: "Aston Martin", logo: "/placeholder.svg?height=100&width=200", color: "bg-green-800" },
    { nombre: "Alpine", logo: "/placeholder.svg?height=100&width=200", color: "bg-blue-700" },
  ]

  return (
    <section id="equipos" className="py-16 bg-black">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-3xl font-bold">EQUIPOS DE F1</h2>
          <button className="border border-red-600 text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded-md">
            VER TODOS LOS EQUIPOS
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {equipos.map((equipo, index) => (
            <TarjetaEquipo key={index} equipo={equipo} />
          ))}
        </div>
      </div>
    </section>
  )
}

