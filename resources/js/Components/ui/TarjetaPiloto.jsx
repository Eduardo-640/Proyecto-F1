"use client"

import { useState, useMemo } from "react"
import { ChevronRight } from "lucide-react"
import { Modal, Button, Tabs, Tab } from "react-bootstrap"
import axios from "axios"

export default function TarjetaPiloto({ piloto, year }) {
  const [showModal, setShowModal] = useState(false)
  const [detallesPiloto, setDetallesPiloto] = useState(null)
  const [loadingDetalles, setLoadingDetalles] = useState(false)

  // Extraer el año de nacimiento de la fecha completa
  const añoNacimiento = piloto.dateOfBirth ? new Date(piloto.dateOfBirth).getFullYear() : "N/A"

  // Función para abrir el modal y cargar los detalles del piloto
  const abrirModal = async () => {
    setShowModal(true)
    setLoadingDetalles(true)
    try {
      const response = await axios.get(`/api/pilotos/${year}/detalles/${piloto.driverId}`)
      setDetallesPiloto(response.data)
    } catch (error) {
      console.error("Error al cargar los detalles del piloto:", error)
      setDetallesPiloto(null)
    } finally {
      setLoadingDetalles(false)
    }
  }

  // Función para cerrar el modal
  const cerrarModal = () => setShowModal(false)

  // Calcular estadísticas destacadas
  const estadisticas = useMemo(() => {
    if (!detallesPiloto) return { victorias: 0, podios: 0, puntosTotales: 0 }

    const victorias = detallesPiloto.filter((carrera) => carrera.Results[0].position === "1").length
    const podios = detallesPiloto.filter((carrera) =>
      ["1", "2", "3"].includes(carrera.Results[0].position)
    ).length
    const puntosTotales = detallesPiloto.reduce(
      (total, carrera) => total + parseFloat(carrera.Results[0].points || 0),
      0
    )

    return { victorias, podios, puntosTotales }
  }, [detallesPiloto])

  return (
    <>
      <div className="bg-gray-800 border border-gray-700 overflow-hidden hover:border-red-600 transition-colors rounded-lg">
        <div className="relative" style={{ width: "420px", height: "450px" }}>
          <img
            src={`/images/imagenes_drivers/${piloto.driverId}.jpg`}
            onError={(e) => {
              e.target.onerror = null; // Evita un bucle infinito si la imagen de respaldo también falla
              e.target.src = "/placeholder.svg"; // Imagen de respaldo
            }}
            alt={`${piloto.givenName} ${piloto.familyName}`}
            className="w-full h-full object-cover"
            style={{ objectPosition: "top" }}
          />
          <div className="absolute bottom-0 left-0 bg-red-600 text-white px-3 py-1 font-bold">
            {piloto.permanentNumber || "N/A"}
          </div>
        </div>
        <div className="p-6">
          <div className="text-sm text-gray-400 mb-2">
            {piloto.nationality} · {añoNacimiento}
          </div>
          <h3 className="text-xl font-bold mb-2 text-white">
            {piloto.givenName} {piloto.familyName}
          </h3>
          <p className="text-gray-300 mb-4">{piloto.Constructor?.name || "Equipo no disponible"}</p>
          <button className="text-red-500 hover:text-red-400 flex items-center" onClick={abrirModal}>
            VER DETALLES <ChevronRight className="h-4 w-4 ml-1" />
          </button>
        </div>
      </div>

      {/* Modal con información detallada */}
      <Modal
        show={showModal}
        onHide={cerrarModal}
        centered
        size="xl"
        contentClassName="border-0 rounded shadow-lg overflow-hidden"
      >
        <div className="bg-dark text-white">
          <Modal.Header closeButton className="bg-dark text-white border-bottom border-danger" closeVariant="white">
            <Modal.Title className="fs-4 fw-bold">
              {piloto.givenName} {piloto.familyName}
            </Modal.Title>
          </Modal.Header>

          <Modal.Body className="bg-dark p-0">
            {loadingDetalles ? (
              <div className="text-center py-5">
                <div className="spinner-border text-danger" role="status">
                  <span className="visually-hidden">Cargando...</span>
                </div>
              </div>
            ) : detallesPiloto ? (
              <Tabs defaultActiveKey="info" className="mb-0 border-0 nav-tabs-dark" fill>
                {/* Pestaña de Información */}
                <Tab
                  eventKey="info"
                  title={
                    <span className="text-white">
                      <i className="bi bi-info-circle me-1"></i>
                      Información
                    </span>
                  }
                >
                  <div className="p-4">
                    <div className="row">
                    {/* Columna izquierda: Foto e información básica */}
                    <div className="col-md-4">
                      {/* Foto del piloto */}
                      <div className="rounded overflow-hidden shadow-sm mb-4" style={{ height: "300px" }}>
                        <img
                          src={`/images/imagenes_drivers/${piloto.driverId}.jpg`}
                          onError={(e) => {
                            e.target.onerror = null; // Evita un bucle infinito si la imagen de respaldo también falla
                            e.target.src = "/placeholder.svg"; // Imagen de respaldo
                          }}
                          alt={`${piloto.givenName} ${piloto.familyName}`}
                          className="w-100 h-100 object-cover"
                          style={{ objectPosition: "top" }} 
                        />
                      </div>

                      {/* Información básica */}
                      <div className="bg-gray-700 bg-opacity-50 rounded shadow-sm p-3 mb-4">
                        <h5 className="border-bottom border-gray-600 pb-2 mb-3">Información Básica</h5>

                        <div className="mb-2">
                          <span className="text-gray-400">Nombre:</span>
                          <span className="float-end text-white">
                            {piloto.givenName} {piloto.familyName}
                          </span>
                        </div>

                        <div className="mb-2">
                          <span className="text-gray-400">Nacionalidad:</span>
                          <span className="float-end text-white">{piloto.nationality}</span>
                        </div>

                        <div className="mb-2">
                          <span className="text-gray-400">Fecha de nacimiento:</span>
                          <span className="float-end text-white">{piloto.dateOfBirth}</span>
                        </div>

                        <div className="mb-2">
                          <span className="text-gray-400">Edad:</span>
                          <span className="float-end text-white">
                            {piloto.dateOfBirth
                              ? new Date().getFullYear() - new Date(piloto.dateOfBirth).getFullYear()
                              : "N/A"}{" "}
                            años
                          </span>
                        </div>

                        <div className="mb-2">
                          <span className="text-gray-400">Número:</span>
                          <span className="float-end">
                            <span className="badge bg-danger">{piloto.permanentNumber}</span>
                          </span>
                        </div>

                        <div className="mb-0">
                          <span className="text-gray-400">Código:</span>
                          <span className="float-end text-white">{piloto.code}</span>
                        </div>
                      </div>

                      {/* Equipo actual */}
                      <div className="bg-gray-700 bg-opacity-50 rounded shadow-sm p-3">
                        <h5 className="border-bottom border-gray-600 pb-2 mb-3">Equipo Actual</h5>

                        <div className="d-flex align-items-center">
                          <div className="rounded overflow-hidden me-3" style={{ width: "3rem", height: "3rem" }}>
                            <div className="w-100 h-100 d-flex align-items-center justify-content-center bg-gray-800">
                              <i className="bi bi-flag-fill text-gray-500" style={{ fontSize: "1.5rem" }}></i>
                            </div>
                          </div>
                          <div>
                            <div className="fw-bold text-white">{piloto.Constructor?.name || "No disponible"}</div>
                            <div className="small text-gray-400">{piloto.Constructor?.nationality || ""}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Columna derecha: Biografía y estadísticas */}
                    <div className="col-md-8">
                      {/* Biografía */}
                      <div className="bg-gray-700 bg-opacity-50 rounded shadow-sm p-4 mb-4">
                        <h4 className="mb-3 fw-bold">Biografía</h4>
                    <p className="text-gray-300 lh-base">
                          {piloto.biografia ||
                            `${piloto.givenName} ${piloto.familyName} es un piloto de Fórmula 1 de nacionalidad ${piloto.nationality}. 
                            Ha demostrado su talento y dedicación en las pistas más exigentes del mundo, 
                            consolidándose como uno de los competidores más respetados del circuito.
                            A lo largo de su carrera, ha logrado importantes victorias y ha representado 
                            a equipos de prestigio en el mundo del automovilismo.`}
                        </p>
                      </div>

                      {/* Estadísticas destacadas */}
                      <div className="bg-gray-700 bg-opacity-50 rounded shadow-sm p-4">
                        <h4 className="mb-3 fw-bold">Estadísticas Destacadas</h4>

                        <div className="row g-3">
                          {/* Victorias */}
                          <div className="col-md-6 col-lg-4">
                            <div className="bg-gray-800 rounded p-3 h-100">
                              <div className="d-flex align-items-center">
                                <div
                                  className="flex-shrink-0 rounded-circle bg-warning bg-opacity-25 d-flex align-items-center justify-content-center text-warning me-3"
                                  style={{ width: "3rem", height: "3rem" }}
                                >
                                  <i className="bi bi-trophy-fill"></i>
                                </div>
                                <div>
                                  <div className="small text-gray-400">Victorias</div>
                                  <div className="fs-4 fw-bold text-white">{estadisticas.victorias}</div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Podios */}
                          <div className="col-md-6 col-lg-4">
                            <div className="bg-gray-800 rounded p-3 h-100">
                              <div className="d-flex align-items-center">
                                <div
                                  className="flex-shrink-0 rounded-circle bg-danger bg-opacity-25 d-flex align-items-center justify-content-center text-danger me-3"
                                  style={{ width: "3rem", height: "3rem" }}
                                >
                                  <i className="bi bi-award-fill"></i>
                                </div>
                                <div>
                                  <div className="small text-gray-400">Podios</div>
                                  <div className="fs-4 fw-bold text-white">{estadisticas.podios}</div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Puntos Totales */}
                          <div className="col-md-6 col-lg-4">
                            <div className="bg-gray-800 rounded p-3 h-100">
                              <div className="d-flex align-items-center">
                                <div
                                  className="flex-shrink-0 rounded-circle bg-success bg-opacity-25 d-flex align-items-center justify-content-center text-success me-3"
                                  style={{ width: "3rem", height: "3rem" }}
                                >
                                  <i className="bi bi-graph-up-arrow"></i>
                                </div>
                                <div>
                                  <div className="small text-gray-400">Puntos</div>
                                  <div className="fs-4 fw-bold text-white">{estadisticas.puntosTotales}</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Tab>

              {/* Pestaña de Resultados */}
              <Tab
                eventKey="resultados"
                title={
                  <span className="text-white">
                    <i className="bi bi-list-ol me-1"></i>
                    Resultados
                  </span>
                }
              >
                <div className="p-4">
                  <h4 className="text-white mb-3 fw-bold">Resultados Recientes</h4>
                  <div className="table-responsive">
                    <table className="table table-dark table-striped table-hover">
                      <thead>
                        <tr>
                          <th>Carrera</th>
                          <th>Posición</th>
                          <th>Puntos</th>
                        </tr>
                      </thead>
                      <tbody>
                        {detallesPiloto && detallesPiloto.length > 0 ? (
                          detallesPiloto.map((carrera, index) => (
                            <tr key={index}>
                              <td>{carrera.raceName}</td>
                              <td>
                                {carrera.Results[0].position === "1" ? (
                                  <span className="badge bg-warning text-dark">
                                    1° <i className="bi bi-trophy-fill ms-1"></i>
                                  </span>
                                ) : carrera.Results[0].position === "2" ? (
                                  <span className="badge bg-secondary">2°</span>
                                ) : carrera.Results[0].position === "3" ? (
                                  <span className="badge bg-danger">3°</span>
                                ) : carrera.Results[0].position === "DNF" ? (
                                  <span className="badge bg-danger">DNF</span>
                                ) : (
                                  carrera.Results[0].position
                                )}
                              </td>
                              <td>{carrera.Results[0].points}</td>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td colSpan="3" className="text-center">
                              No hay resultados disponibles
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                  </div>
              </Tab>
              </Tabs>
            ) : (
              <div className="text-center py-5">
                <p className="text-gray-400">No se pudieron cargar los detalles del piloto.</p>
              </div>
            )}
          </Modal.Body>

          <Modal.Footer className="bg-dark border-0 justify-content-center">
            <Button variant="danger" onClick={cerrarModal} className="px-5 py-2 fw-bold text-white shadow">
              Cerrar
            </Button>
          </Modal.Footer>
        </div>
      </Modal>

      {/* Estilos para las pestañas */}
      <style>
        {`
        .nav-tabs-dark {
            background-color: #212529;
        }
        .nav-tabs-dark .nav-link {
            border: none;
            color: #adb5bd;
            padding: 0.75rem 1rem;
            border-radius: 0;
        }
        .nav-tabs-dark .nav-link.active {
            background-color: #343a40;
            color: white;
            border: none;
        }
        .nav-tabs-dark .nav-link:hover:not(.active) {
            background-color: #343a40;
            color: white;
        }
        `}
      </style>
    </>
  )
}

