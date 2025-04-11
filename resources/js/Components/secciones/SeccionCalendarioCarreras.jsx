import { useEffect, useState } from "react";
import { Modal, Button, Tabs, Tab } from "react-bootstrap"
import TarjetaCarrera from "../ui/TarjetaCarrera";

export default function SeccionCalendarioCarreras() {
  const [carreras, setCarreras] = useState([]);
  const [carrerasCompletas, setCarrerasCompletas] = useState([]);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false)

  useEffect(() => {
    // Realizar la solicitud a la API
    const fetchCarreras = async () => {
      try {
        const response = await fetch("/api/calendarioCarreras");
        if (!response.ok) {
          throw new Error("Error al obtener las carreras");
        }
        const data = await response.json();

        // Verificar si la API devolvió un mensaje o un error
        if (data.message || data.error) {
          setError(data.message || data.error);
          setCarreras([]);
          setCarrerasCompletas([]);
        } else {
          // Tomar solo las primeras 6 carreras
          const carrerasFuturas = Array.isArray(data) ? data.slice(0, 6) : [];
          setCarreras(carrerasFuturas);

          // Guardar todas las carreras para el modal
          setCarrerasCompletas(Array.isArray(data) ? data : []);
        }
      } catch (error) {
        console.error("Error al cargar las carreras:", error);
        setError("No se pudieron cargar las carreras.");
      }
    };

    fetchCarreras();
  }, []);

  const fechaActual = new Date().getFullYear();

  return (
    <section id="carreras" className="py-16 bg-gray-900">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center mb-10">
          <h2 className="text-3xl font-bold">CALENDARIO {fechaActual}</h2>
          <button
            className="border border-red-600 text-red-600 hover:bg-red-600 hover:text-white px-4 py-2 rounded-md"
            onClick={() => setShowModal(true)}
          >
            VER CALENDARIO COMPLETO
          </button>
        </div>

        {error ? (
          <p className="text-white text-center">{error}</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {carreras.map((carrera, index) => (
              <TarjetaCarrera key={index} carrera={carrera} />
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      <Modal
        show={showModal}
        onHide={() => setShowModal(false)}
        centered
        size="xl"
        contentClassName="border-0 rounded shadow-lg overflow-hidden"
      >
        <div className="bg-dark text-white">
          <Modal.Header closeButton className="bg-dark text-white border-bottom border-danger" closeVariant="white">
            <Modal.Title className="text-xl font-bold">Calendario Completo</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {carrerasCompletas.map((carrera, index) => (
                <TarjetaCarrera key={index} carrera={carrera} />
              ))}
            </div>
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
    </section>
  );
}
