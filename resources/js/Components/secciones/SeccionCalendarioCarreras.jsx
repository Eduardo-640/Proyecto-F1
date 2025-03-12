import TarjetaCarrera from "../ui/tarjeta-carrera";

export default function SeccionCalendarioCarreras() {
    const carreras = [
        { nombre: "Gran Premio de Bahrein", fecha: "2-4 MAR", ubicacion: "Sakhir", bandera: "BH" },
        { nombre: "Gran Premio de Arabia Saudita", fecha: "9-11 MAR", ubicacion: "Jeddah", bandera: "SA" },
        { nombre: "Gran Premio de Australia", fecha: "23-25 MAR", ubicacion: "Melbourne", bandera: "AU" },
        { nombre: "Gran Premio de Japón", fecha: "6-8 ABR", ubicacion: "Suzuka", bandera: "JP" },
        { nombre: "Gran Premio de China", fecha: "20-22 ABR", ubicacion: "Shanghai", bandera: "CN" },
        { nombre: "Gran Premio de Miami", fecha: "4-6 MAY", ubicacion: "Miami", bandera: "US" }
    ];    

  return (
    <section id="carreras" className="py-16 bg-gray-900">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-3xl font-bold">CALENDARIO 2025</h2>
          <button className="border border-red-600 text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded-md">
            VER CALENDARIO COMPLETO
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {carreras.map((carrera, index) => (
            <TarjetaCarrera key={index} carrera={carrera} />
          ))}
        </div>
      </div>
    </section>
  )
}
