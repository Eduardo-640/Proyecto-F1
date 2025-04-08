"use client"

import { useState, useEffect } from "react"
import axios from "axios"
import { Modal, Button, Tabs, Tab } from "react-bootstrap"
import GraficaBarras from "@/Components/ui/GraficaBarras"
import Podio from "@/Components/ui/Podio"

const Carreras = () => {
  const [year, setYear] = useState(new Date().getFullYear())
  const [carreras, setCarreras] = useState([])
  const [loading, setLoading] = useState(true)
  const [carreraSeleccionada, setCarreraSeleccionada] = useState(null)
  const [graficaDatos, setGraficaDatos] = useState(null);
  const [showModal, setShowModal] = useState(false)
  const years = Array.from({ length: 6 }, (_, i) => new Date().getFullYear() - i)

  useEffect(() => {
    const fetchCarreras = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/carreras/${year}`);
        console.log("Respuesta de la API:", response.data); // Verifica qué datos llegan
        setCarreras(response.data || []);
      } catch (error) {
        console.error("Error al obtener las carreras:", error);
        setCarreras([]); // Evitar problemas si la API falla
      } finally {
        setLoading(false);
      }
    };

    fetchCarreras();
  }, [year]);

  const verCarrera = async (year, round) => {
    try {
      const response = await axios.get(`/api/carrera/${year}/${round}`);
      const data = response.data;

      // Extraer las 3 primeras posiciones para el podio
      const podio = data.resultados.slice(0, 3).map((piloto) => ({
        piloto: `${piloto.Driver.givenName} ${piloto.Driver.familyName}`,
        equipo: piloto.Constructor.name,
        tiempo: piloto.Time?.time || "No disponible",
      }));

      console.log("Podio:", podio); // Verificar el array del podio

      // Crear los datos para la gráfica de barras
      const datosGrafica = {
        labels: data.resultados.map(
          (piloto) => `${piloto.Driver.givenName} ${piloto.Driver.familyName}`
        ),
        data: data.resultados.map((piloto) => parseInt(piloto.points, 10)),
      };

      console.log("Datos de la gráfica:", datosGrafica); // Verificar los datos de la gráfica

      // Combinar podio y datos de la gráfica en un solo objeto
      const detallesCarrera = {
        ...data,
        podio: podio,
        grafica: datosGrafica,
      };

      // Actualizar el estado con los datos combinados
      setCarreraSeleccionada(detallesCarrera);

      setShowModal(true); // Muestra el modal con los detalles
    } catch (error) {
      console.error("Error al obtener los detalles de la carrera", error);
    }
  };

  // Función para formatear la fecha
  const formatearFecha = (fechaStr) => {
    if (!fechaStr) return "No disponible"
    const fecha = new Date(fechaStr)
    return fecha.toLocaleDateString("es-ES", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  // Función para formatear la hora
  const formatearHora = (fechaStr, horaStr) => {
    if (!fechaStr || !horaStr) return "No disponible"
    const fechaHora = new Date(`${fechaStr}T${horaStr}`)
    return (
      fechaHora.toLocaleTimeString("es-ES", {
        hour: "2-digit",
        minute: "2-digit",
      }) + " (hora local)"
    )
  }

  return (
    <div className="container mt-4">
      <h1 className="text-center">Calendario de Carreras {year}</h1>

      {/* Selector de año */}
      <div className="text-center my-3">
        <label className="me-2 fs-4 fw-bold">Selecciona un año:</label>
        <select
          className="form-select form-select-lg d-inline-block w-auto text-white bg-dark"
          value={year}
          onChange={(e) => setYear(e.target.value)}
        >
          {years.map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {/* Mostrar mensaje de carga */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-600 mr-3"></div>
          <p className="text-white font-medium">Cargando carreras...</p>
        </div>
      )}

      {/* Lista de carreras */}
      <div className="row">
        {/* Mensaje si no hay Carreras */}
        {!loading && carreras.length === 0 && (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center my-8">
            <i className="bi bi-exclamation-triangle-fill text-yellow-500 text-3xl mb-3"></i>
            <p className="text-white text-lg">No hay carreras disponibles para la temporada {year}.</p>
          </div>
        )}

        {carreras.map((carrera, index) => (
          <div key={index} className="col-md-4 mb-4">
            <div className="card shadow">
              <div className="card-body text-white bg-dark border border-secondary hover:border-danger transition-colors rounded">
                <h5 className="card-title">{carrera.raceName || "Nombre no disponible"}</h5>
                <p className="card-text">
                  Circuito: {carrera.Circuit?.circuitName || "Sin datos"}
                </p>
                <Button variant="danger" onClick={() => verCarrera(year, carrera.round)}>
                  Ver detalles
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal para detalles de la carrera */}
      <Modal
        show={showModal}
        onHide={() => setShowModal(false)}
        centered
        size="xl"
        contentClassName="border-0 rounded shadow-lg overflow-hidden"
      >
        <div className="bg-dark text-white">
          <Modal.Header closeButton className="bg-dark text-white border-bottom border-danger" closeVariant="white">
            <Modal.Title className="fs-4 fw-bold">
              {carreraSeleccionada?.detalles?.raceName || "Detalles de la carrera"}
            </Modal.Title>
          </Modal.Header>

          <Modal.Body className="bg-dark p-0">
            {carreraSeleccionada ? (
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
                    {/* Imagen del circuito */}
                    <div
                      className="w-100 mb-4 rounded overflow-hidden shadow-sm bg-secondary"
                      style={{ width: "490px", height: "400px" }}
                    >
                      <img
                        src={`/images/imagenes_races/${carreraSeleccionada.detalles?.raceName}.png`}
                        alt={carreraSeleccionada.detalles?.Circuit?.circuitName || "Sin datos"}
                        onError={(e) => {
                          e.target.onerror = null; // Evita un bucle infinito si la imagen de respaldo también falla
                          e.target.src = "/placeholder.svg"; // Imagen de respaldo
                        }}
                        className="w-full h-full object-contain"
                      />
                    </div>

                    {/* Información de la carrera */}
                    <div className="bg-secondary bg-opacity-25 rounded shadow-sm p-4 text-white">
                      {/* Circuito */}
                      <div className="d-flex align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <div
                          className="flex-shrink-0 rounded-circle bg-danger bg-opacity-25 d-flex align-items-center justify-content-center text-danger me-3"
                          style={{ width: "2.5rem", height: "2.5rem" }}
                        >
                          <i className="bi bi-geo-alt-fill"></i>
                        </div>
                        <div>
                          <div className="small text-gray-400 fw-medium">Circuito</div>
                          <div className="text-white fw-bold">
                            {carreraSeleccionada.detalles?.Circuit?.circuitName || "Sin datos"}
                          </div>
                        </div>
                      </div>

                      {/* Ubicación */}
                      <div className="d-flex align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <div
                          className="flex-shrink-0 rounded-circle bg-primary bg-opacity-25 d-flex align-items-center justify-content-center text-primary me-3"
                          style={{ width: "2.5rem", height: "2.5rem" }}
                        >
                          <i className="bi bi-pin-map-fill"></i>
                        </div>
                        <div>
                          <div className="small text-gray-400 fw-medium">Ubicación</div>
                          <div className="text-white">
                            {carreraSeleccionada.detalles?.Circuit?.Location?.locality || "Sin datos"},{" "}
                            {carreraSeleccionada.detalles?.Circuit?.Location?.country || "Sin datos"}
                          </div>
                        </div>
                      </div>

                      {/* Fecha */}
                      <div className="d-flex align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <div
                          className="flex-shrink-0 rounded-circle bg-success bg-opacity-25 d-flex align-items-center justify-content-center text-success me-3"
                          style={{ width: "2.5rem", height: "2.5rem" }}
                        >
                          <i className="bi bi-calendar-event-fill"></i>
                        </div>
                        <div>
                          <div className="small text-gray-400 fw-medium">Fecha</div>
                          <div className="text-white">
                            {formatearFecha(carreraSeleccionada.detalles?.date)}
                          </div>
                        </div>
                      </div>

                      {/* Hora */}
                      <div className="d-flex align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <div
                          className="flex-shrink-0 rounded-circle bg-info bg-opacity-25 d-flex align-items-center justify-content-center text-info me-3"
                          style={{ width: "2.5rem", height: "2.5rem" }}
                        >
                          <i className="bi bi-clock-fill"></i>
                        </div>
                        <div>
                          <div className="small text-gray-400 fw-medium">Hora</div>
                          <div className="text-white">
                            {carreraSeleccionada.detalles?.time
                              ? formatearHora(
                                carreraSeleccionada.detalles?.date,
                                carreraSeleccionada.detalles?.time
                              )
                              : "No disponible"}
                          </div>
                        </div>
                      </div>

                      {/* Descripción */}
                      <div className="d-flex align-items-start">
                        <div
                          className="flex-shrink-0 rounded-circle bg-warning bg-opacity-25 d-flex align-items-center justify-content-center text-warning me-3"
                          style={{ width: "2.5rem", height: "2.5rem" }}
                        >
                          <i className="bi bi-chat-quote-fill"></i>
                        </div>
                        <div>
                          <div className="small text-gray-400 fw-medium">Descripción</div>
                          <div className="text-white small mt-1 lh-base">
                            {carreraSeleccionada.detalles?.descripcion || "Sin datos"}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Tab>

                {/* Pestaña de Estadísticas */}
                <Tab
                  eventKey="estadisticas"
                  title={
                    <span className="text-white">
                      <i className="bi bi-bar-chart-fill me-1"></i>
                      Estadísticas
                    </span>
                  }
                >
                  <div className="p-4">
                    {carreraSeleccionada && carreraSeleccionada.resultados && (
                      <GraficaBarras
                        datos={{
                          labels: carreraSeleccionada.resultados.map(
                            (piloto) => `${piloto.Driver.givenName} ${piloto.Driver.familyName}`
                          ),
                          data: carreraSeleccionada.resultados.map((piloto) =>
                            parseInt(piloto.points, 10)
                          ),
                        }}
                      />
                    )}
                  </div>
                </Tab>

                {/* Pestaña de Podio */}
                <Tab
                  eventKey="podio"
                  title={
                    <span className="text-white">
                      <i className="bi bi-trophy-fill me-1"></i>
                      Podio
                    </span>
                  }
                >
                  <div className="p-4">
                    <Podio ganadores={carreraSeleccionada.podio} />
                  </div>
                </Tab>
              </Tabs>
            ) : (
              <div className="d-flex justify-content-center align-items-center py-5 bg-dark text-white">
                <div className="spinner-border text-danger me-3" role="status">
                  <span className="visually-hidden">Cargando...</span>
                </div>
                <p className="m-0 text-gray-300 fw-medium">Cargando información de la carrera...</p>
              </div>
            )}
          </Modal.Body>

          <Modal.Footer className="bg-dark border-0 justify-content-center">
            <Button
              variant="danger"
              onClick={() => setShowModal(false)}
              className="px-5 py-2 fw-bold text-white shadow"
            >
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
    </div>
  )
}

export default Carreras