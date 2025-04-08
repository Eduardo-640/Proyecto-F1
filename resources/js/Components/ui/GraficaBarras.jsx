const GraficaBarras = ({ datos }) => {
    if (!datos) return null
    const maxValue = Math.max(...datos.data)

    return (
      <div className="mt-4">
        <h4 className="text-white mb-3 font-bold">Puntos por Piloto</h4>
        <div className="space-y-3">
          {datos.labels.map((label, index) => (
            <div key={index} className="d-flex align-items-center">
              <div className="w-24 text-gray-300 text-sm">{label}</div>
              <div className="flex-grow-1">
                <div className="h-6 bg-gray-800 rounded-pill overflow-hidden">
                  <div
                    className="h-100 bg-danger rounded-pill"
                    style={{ width: `${(datos.data[index] / maxValue) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div className="w-12 text-end text-white fw-bold ms-2">{datos.data[index]}</div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  export default GraficaBarras