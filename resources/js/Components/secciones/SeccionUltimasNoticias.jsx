import TarjetaNoticia from "../ui/TarjetaNoticia"

export default function SeccionUltimasNoticias() {
  const articulos = [
    {
      titulo: "Verstappen domina en Mónaco",
      extracto: "Max Verstappen aseguró su cuarta victoria de la temporada con una actuación dominante en Mónaco.",
      fecha: "28 MAYO 2025",
      img: "/placeholder.svg?height=300&width=500",
    },
    {
      titulo: "Ferrari presenta importante paquete de mejoras",
      extracto: "Ferrari ha introducido un importante paquete de mejoras antes del Gran Premio de España.",
      fecha: "20 MAYO 2025",
      img: "/placeholder.svg?height=300&width=500",
    },
    {
      titulo: "Hamilton firma extensión de contrato",
      extracto: "Lewis Hamilton ha firmado una extensión de contrato de dos años con Mercedes.",
      fecha: "15 MAYO 2025",
      img: "/placeholder.svg?height=300&width=500",
    },
  ]

  return (
    <section id="noticias" className="py-16 bg-gradient-to-b from-black to-gray-900">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-3xl font-bold">ÚLTIMAS NOTICIAS</h2>
          <button className="border border-red-600 text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded-md">
            VER TODAS LAS NOTICIAS
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {articulos.map((articulo, index) => (
            <TarjetaNoticia key={index} articulo={articulo} />
          ))}
        </div>
      </div>
    </section>
  )
}

