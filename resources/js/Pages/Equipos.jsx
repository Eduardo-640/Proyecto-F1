"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Modal, Tabs, Tab } from "react-bootstrap";
import Navbar from '@/Components/cabeceras/Navbar';

const Equipos = () => {
  const [equipos, setEquipos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [equipoSeleccionado, setEquipoSeleccionado] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const currentYear = new Date().getFullYear(); // Año actual

  // Mapeo de colores para los equipos
  const coloresEquipos = {
    "Alpine F1 Team": "bg-blue-600",
    "Aston Martin": "bg-green-600",
    "Ferrari": "bg-red-600",
    "Haas F1 Team": "bg-gray-500",
    "McLaren": "bg-orange-500",
    "Mercedes": "bg-gray-800",
    "RB F1 Team": "bg-purple-600", 
    "Red Bull": "bg-red-500",
    "Sauber": "bg-teal-600", 
    "Williams": "bg-cyan-600",
  };

  // Agregar lógica para obtener datos del diccionario
  const datosEquipos = {
    "Alpine F1 Team": {
        "drivers": [
            {
                "driverId": "gasly",
                "name": "Pierre Gasly",
                "nationality": "French",
                "url": "http://en.wikipedia.org/wiki/Pierre_Gasly"
            },
            {
                "driverId": "oconnor",
                "name": "Esteban Ocon",
                "nationality": "French",
                "url": "http://en.wikipedia.org/wiki/Esteban_Ocon"
            }
        ],
        "teamPrincipal": {
            "name": "Otmar Szafnauer",
            "url": "http://en.wikipedia.org/wiki/Otmar_Szafnauer"
        }
    },
    "Aston Martin": {
        "drivers": [
            {
                "driverId": "stroll",
                "name": "Lance Stroll",
                "nationality": "Canadian",
                "url": "http://en.wikipedia.org/wiki/Lance_Stroll"
            },
            {
                "driverId": "alonso",
                "name": "Fernando Alonso",
                "nationality": "Spanish",
                "url": "http://en.wikipedia.org/wiki/Fernando_Alonso"
            }
        ],
        "teamPrincipal": {
            "name": "Mike Krack",
            "url": "http://en.wikipedia.org/wiki/Mike_Krack_(motorsport)"
        }
    },
    "Ferrari": {
        "drivers": [
            {
                "driverId": "leclerc",
                "name": "Charles Leclerc",
                "nationality": "Monacan",
                "url": "http://en.wikipedia.org/wiki/Charles_Leclerc"
            },
            {
                "driverId": "sainz",
                "name": "Carlos Sainz",
                "nationality": "Spanish",
                "url": "http://en.wikipedia.org/wiki/Carlos_Sainz_Jr."
            }
        ],
        "teamPrincipal": {
            "name": "Frédéric Vasseur",
            "url": "http://en.wikipedia.org/wiki/Fr%C3%A9d%C3%A9ric_Vasseur"
        }
    },
    "Haas F1 Team": {
        "drivers": [
            {
                "driverId": "magnussen",
                "name": "Kevin Magnussen",
                "nationality": "Danish",
                "url": "http://en.wikipedia.org/wiki/Kevin_Magnussen"
            },
            {
                "driverId": "hulkenberg",
                "name": "Nico Hülkenberg",
                "nationality": "German",
                "url": "http://en.wikipedia.org/wiki/Nico_H%C3%BClkenberg"
            }
        ],
        "teamPrincipal": {
            "name": "Guenther Steiner",
            "url": "http://en.wikipedia.org/wiki/Guenther_Steiner"
        }
    },
    "McLaren": {
        "drivers": [
            {
                "driverId": "norris",
                "name": "Lando Norris",
                "nationality": "British",
                "url": "http://en.wikipedia.org/wiki/Lando_Norris"
            },
            {
                "driverId": "piastri",
                "name": "Oscar Piastri",
                "nationality": "Australian",
                "url": "http://en.wikipedia.org/wiki/Oscar_Piastri"
            }
        ],
        "teamPrincipal": {
            "name": "Andreas Seidl",
            "url": "http://en.wikipedia.org/wiki/Andreas_Seidl"
        }
    },
    "Mercedes": {
        "drivers": [
            {
                "driverId": "hamilton",
                "name": "Lewis Hamilton",
                "nationality": "British",
                "url": "http://en.wikipedia.org/wiki/Lewis_Hamilton"
            },
            {
                "driverId": "russell",
                "name": "George Russell",
                "nationality": "British",
                "url": "http://en.wikipedia.org/wiki/George_Russell"
            }
        ],
        "teamPrincipal": {
            "name": "Toto Wolff",
            "url": "http://en.wikipedia.org/wiki/Toto_Wolff"
        }
    },
    "RB F1 Team": {
        "drivers": [
            {
                "driverId": "perez",
                "name": "Sergio Pérez",
                "nationality": "Mexican",
                "url": "http://en.wikipedia.org/wiki/Sergio_P%C3%A9rez"
            },
            {
                "driverId": "verstappen",
                "name": "Max Verstappen",
                "nationality": "Dutch",
                "url": "http://en.wikipedia.org/wiki/Max_Verstappen"
            }
        ],
        "teamPrincipal": {
            "name": "Christian Horner",
            "url": "http://en.wikipedia.org/wiki/Christian_Horner"
        }
    },
    "Red Bull": {
        "drivers": [
            {
                "driverId": "perez",
                "name": "Sergio Pérez",
                "nationality": "Mexican",
                "url": "http://en.wikipedia.org/wiki/Sergio_P%C3%A9rez"
            },
            {
                "driverId": "verstappen",
                "name": "Max Verstappen",
                "nationality": "Dutch",
                "url": "http://en.wikipedia.org/wiki/Max_Verstappen"
            }
        ],
        "teamPrincipal": {
            "name": "Christian Horner",
            "url": "http://en.wikipedia.org/wiki/Christian_Horner"
        }
    },
    "Sauber": {
        "drivers": [
            {
                "driverId": "bottas",
                "name": "Valtteri Bottas",
                "nationality": "Finnish",
                "url": "http://en.wikipedia.org/wiki/Valtteri_Bottas"
            },
            {
                "driverId": "zhou",
                "name": "Zhou Guanyu",
                "nationality": "Chinese",
                "url": "http://en.wikipedia.org/wiki/Zhou_Guanyu"
            }
        ],
        "teamPrincipal": {
            "name": "Frédéric Vasseur",
            "url": "http://en.wikipedia.org/wiki/Fr%C3%A9d%C3%A9ric_Vasseur"
        }
    },
    "Williams": {
        "drivers": [
            {
                "driverId": "albon",
                "name": "Alex Albon",
                "nationality": "Thai-British",
                "url": "http://en.wikipedia.org/wiki/Alex_Albon"
            },
            {
                "driverId": "sargeant",
                "name": "Logan Sargeant",
                "nationality": "American",
                "url": "http://en.wikipedia.org/wiki/Logan_Sargeant"
            }
        ],
        "teamPrincipal": {
            "name": "James Vowles",
            "url": "http://en.wikipedia.org/wiki/James_Vowles"
        }
    }
}


  const obtenerDatosEquipo = (nombreEquipo) => {
    const clave = nombreEquipo//.toLowerCase().replace(/\s+/g, "_");
    return datosEquipos[clave] || null;
  };

  useEffect(() => {
    const fetchEquipos = async () => {
      setLoading(true);
      try {
        const response = await axios.get(`/api/equipos/${currentYear}`);
        setEquipos(response.data || []);
      } catch (error) {
        console.error("Error al obtener los equipos:", error);
        setEquipos([]); // Evitar problemas si la API falla
      } finally {
        setLoading(false);
      }
    };

    fetchEquipos();
  }, [currentYear]);

  const verEquipo = (equipo) => {
    const datosEquipo = obtenerDatosEquipo(equipo.name);
    setEquipoSeleccionado({ ...equipo, datos: datosEquipo });
    setShowModal(true);
  };

  // Función para obtener el color de fondo según el equipo
  const obtenerColorFondo = (nombreEquipo) => {
    console.log("Nombre del equipo:", nombreEquipo); // Depuración
    const color = coloresEquipos[nombreEquipo];
    console.log("Color asignado:", color || "bg-gray-700"); // Depuración
    return color || "bg-gray-700"; // Color por defecto si no está en el mapeo
  };

  return (
    <>
      <Navbar />
    <div className="container mt-4">
      <h1 className="text-center">Equipos de F1 - Temporada {currentYear}</h1>

      {/* Mostrar mensaje de carga */}
      {loading && (
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-red-600 mr-3"></div>
          <p className="text-white font-medium">Cargando equipos...</p>
        </div>
      )}

      {/* Lista de equipos */}
      <div className="row">
        {/* Mensaje si no hay equipos */}
        {!loading && equipos.length === 0 && (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center my-8">
            <i className="bi bi-exclamation-triangle-fill text-yellow-500 text-3xl mb-3"></i>
            <p className="text-white text-lg">No hay equipos disponibles para la temporada {currentYear}.</p>
          </div>
        )}

        {equipos.map((equipo, index) => (
          <div
            key={index}
            className="col-md-4 mb-4"
            onClick={() => verEquipo(equipo)} // Hacer clic en toda la tarjeta
          >
            <div className={`card `}>
              <div className={`card-body ${obtenerColorFondo(equipo.name)} text-white border border-secondary hover:border-danger transition-colors rounded`}>
                <h5 className="card-title">{equipo.name || "Nombre no disponible"}</h5>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal para detalles del equipo */}
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
              {equipoSeleccionado?.name || "Detalles del equipo"}
            </Modal.Title>
          </Modal.Header>

          <Modal.Body className="bg-dark p-0">
            {equipoSeleccionado ? (
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
                    <div className="bg-secondary bg-opacity-25 rounded shadow-sm p-4 text-white">
                      {/* Director */}
                      <div className="d-flex align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <div
                          className="flex-shrink-0 rounded-circle bg-primary bg-opacity-25 d-flex align-items-center justify-content-center text-primary me-3"
                          style={{ width: "2.5rem", height: "2.5rem" }}
                        >
                          <i className="bi bi-person-fill"></i>
                        </div>
                        <div>
                          <div className="small text-gray-400 fw-medium">Director</div>
                          <div className="text-white">
                            {equipoSeleccionado.datos?.teamPrincipal?.name || "Sin datos"}
                          </div>
                        </div>
                      </div>

                      {/* Pilotos */}
                      <div className="d-flex align-items-center mb-3 pb-3 border-bottom border-secondary">
                        <div
                          className="flex-shrink-0 rounded-circle bg-success bg-opacity-25 d-flex align-items-center justify-content-center text-success me-3"
                          style={{ width: "2.5rem", height: "2.5rem" }}
                        >
                          <i className="bi bi-people-fill"></i>
                        </div>
                        <div>
                          <div className="small text-gray-400 fw-medium">Pilotos</div>
                          <div className="text-white">
                            {equipoSeleccionado.datos?.drivers?.map((driver) => (
                              <div key={driver.driverId}>
                                <a href={driver.url} target="_blank" rel="noopener noreferrer" className="text-info">
                                  {driver.name}
                                </a> ({driver.nationality})
                              </div>
                            )) || "Sin datos"}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Tab>

              </Tabs>
            ) : (
              <div className="d-flex justify-content-center align-items-center py-5 bg-dark text-white">
                <div className="spinner-border text-danger me-3" role="status">
                  <span className="visually-hidden">Cargando...</span>
                </div>
                <p className="m-0 text-gray-300 fw-medium">Cargando información del equipo...</p>
              </div>
            )}
          </Modal.Body>

          <Modal.Footer className="bg-dark border-0 justify-content-center">
            <button
              className="btn btn-danger px-5 py-2 fw-bold text-white shadow"
              onClick={() => setShowModal(false)}
            >
              Cerrar
            </button>
          </Modal.Footer>
        </div>
      </Modal>
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
    </>
  );
};

export default Equipos;