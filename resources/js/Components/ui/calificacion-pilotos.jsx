export default function ClasificacionPilotos() {
    const pilotos = [
      { pos: 1, piloto: "Max Verstappen", nacionalidad: "HOL", equipo: "Red Bull Racing", puntos: 170 },
      { pos: 2, piloto: "Charles Leclerc", nacionalidad: "MON", equipo: "Ferrari", puntos: 150 },
      { pos: 3, piloto: "Lando Norris", nacionalidad: "GBR", equipo: "McLaren", puntos: 130 },
      { pos: 4, piloto: "Lewis Hamilton", nacionalidad: "GBR", equipo: "Mercedes", puntos: 120 },
      { pos: 5, piloto: "Carlos Sainz", nacionalidad: "ESP", equipo: "Ferrari", puntos: 110 },
    ]
  
    return (
      <div className="bg-gray-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-900">
                <th className="py-4 px-6 text-left">POS</th>
                <th className="py-4 px-6 text-left">PILOTO</th>
                <th className="py-4 px-6 text-left">NACIONALIDAD</th>
                <th className="py-4 px-6 text-left">EQUIPO</th>
                <th className="py-4 px-6 text-right">PUNTOS</th>
              </tr>
            </thead>
            <tbody>
              {pilotos.map((piloto, index) => (
                <tr key={index} className="border-t border-gray-700 hover:bg-gray-700">
                  <td className="py-4 px-6">{piloto.pos}</td>
                  <td className="py-4 px-6 font-medium">{piloto.piloto}</td>
                  <td className="py-4 px-6">{piloto.nacionalidad}</td>
                  <td className="py-4 px-6">{piloto.equipo}</td>
                  <td className="py-4 px-6 text-right font-bold">{piloto.puntos}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }
  
  