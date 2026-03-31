import AuthenticatedLayout from '@/layouts/AuthLayout';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar';
import { useState } from 'react';


export default function Dashboard() {
    const { user } = useAuth();

    const title = user?.name || user?.email || 'Dashboard';
    // Definir aquí los items del sidebar para que el componente padre los controle
    const sidebarItems = [
        { key: 'overview', label: 'Resumen', href: '/dashboard' },
        { key: 'upgrades', label: 'Mejoras', href: '/upgrades' },
        { key: 'results', label: 'Resultados', href: '/results' },
        { key: 'cars', label: 'Coches', href: '/cars' },
        { key: 'sponsors', label: 'Sponsors', href: '/sponsors' },
        { key: 'balances', label: 'Balances', href: '/balances' },
    ]

    const [selectedSection, setSelectedSection] = useState(sidebarItems[0].key);

    function renderMain() {
        switch (selectedSection) {
            case 'races':
                return <div>Sección: Carreras (contenido controlado por Dashboard)</div>
            case 'teams':
                return <div>Sección: Equipos</div>
            case 'drivers':
                return <div>Sección: Pilotos</div>
            case 'settings':
                return <div>Sección: Ajustes</div>
            default:
                return <div>Sección: Inicio</div>
        }
    }

    return (
        <AuthenticatedLayout
            header={
                <h2 className="text-xl font-semibold leading-tight text-gray-800">
                    {title}
                </h2>
            }
        >
            <div className="flex min-h-[70vh]">
                <Sidebar items={sidebarItems} selected={selectedSection} onSelect={setSelectedSection} />
                <main className="flex-1 p-6">
                    {renderMain()}
                </main>
            </div>
        </AuthenticatedLayout>
    );
}
