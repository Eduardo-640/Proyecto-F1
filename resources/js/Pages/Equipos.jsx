"use client";

import { useState, useEffect } from "react"
import axios from "axios"
import { Modal, Button, Tabs, Tab } from "react-bootstrap"


const Equipos = () => {

    const [equipos, setEquipos] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [selectedEquipo, setSelectedEquipo] = useState(null)
    const [tabKey, setTabKey] = useState("")
    
    useEffect(() => {
        fetchEquipos()
    }, [])
    
    const fetchEquipos = async () => {
        try {
        const response = await axios.get("/api/equipos/2024")
        setEquipos(response.data)
        } catch (error) {
        console.error("Error fetching equipos:", error)
        }
    }
    
    const handleShowModal = (equipo) => {
        setSelectedEquipo(equipo)
        setShowModal(true)
    }
    
    const handleCloseModal = () => {
        setShowModal(false)
        setSelectedEquipo(null)
    }
    
    return (
        <div>
        <h1>Equipos</h1>
        <ul>
            {equipos.map((equipo) => (
            <li key={equipo.id} onClick={() => handleShowModal(equipo)}>
                {equipo.name}
            </li>
            ))}
        </ul>
    
        <Modal show={showModal} onHide={handleCloseModal}>
            <Modal.Header closeButton>
            <Modal.Title>{selectedEquipo?.name}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
            <Tabs activeKey={tabKey} onSelect={(k) => setTabKey(k)}>
                <Tab eventKey="info" title="Info">
                <p>{selectedEquipo?.info}</p>
                </Tab>
                <Tab eventKey="details" title="Details">
                <p>{selectedEquipo?.details}</p>
                </Tab>
            </Tabs>
            </Modal.Body>
            <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
                Close
            </Button>
            </Modal.Footer>
        </Modal>
        </div>
    )
}

export default Equipos