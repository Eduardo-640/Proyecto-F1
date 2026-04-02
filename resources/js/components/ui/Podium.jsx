const Podio = ({ ganadores }) => {
    if (!ganadores || ganadores.length < 3) return null

    return (
      <div className="mt-4">
        <h4 className="text-white mb-4 font-bold">Podio</h4>
        <div className="d-flex justify-content-center align-items-end" style={{ height: "16rem" }}>
          {/* Segundo lugar */}
          <div className="w-100 px-2" style={{ maxWidth: "33.333%" }}>
            <div className="d-flex flex-column align-items-center">
              <div className="text-center">
                <div className="text-gray-300 big">2º</div>
                <div className="text-white fw-bold big">{ganadores[1].piloto}</div>
                <div className="text-gray-400 big">{ganadores[1].equipo}</div>
                <div className="text-gray-300 big mt-1">{ganadores[1].tiempo}</div>
              </div>
            </div>
            <div className="bg-secondary rounded-top" style={{ height: "8rem" }}></div>
          </div>

          {/* Primer lugar */}
          <div className="w-100 px-2" style={{ maxWidth: "33.333%" }}>
            <div className="d-flex flex-column align-items-center">
              <div className="text-center">
                <div className="text-warning big">1º</div>
                <div className="text-white fw-bold">{ganadores[0].piloto}</div>
                <div className="text-gray-400 big">{ganadores[0].equipo}</div>
                <div className="text-gray-300 big mt-1">{ganadores[0].tiempo}</div>
              </div>
            </div>
            <div className="bg-warning rounded-top" style={{ height: "12rem" }}></div>
          </div>

          {/* Tercer lugar */}
          <div className="w-100 px-2" style={{ maxWidth: "33.333%" }}>
            <div className="d-flex flex-column align-items-center">
              <div className="text-center">
                <div className="big" style={{ color: "#CD7F32" }}>
                  3º
                </div>
                <div className="text-white fw-bold big">{ganadores[2].piloto}</div>
                <div className="text-gray-400 big">{ganadores[2].equipo}</div>
                <div className="text-gray-300 big mt-1">{ganadores[2].tiempo}</div>
              </div>
            </div>
            <div className="rounded-top" style={{ height: "4rem", backgroundColor: "#CD7F32" }}></div>
          </div>
        </div>
      </div>
    )
  }

export default Podio