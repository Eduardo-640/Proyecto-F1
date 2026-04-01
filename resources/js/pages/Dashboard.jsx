import AuthenticatedLayout from '@/layouts/AuthLayout';
import { useAuth } from '@/context/AuthContext';
import Sidebar from '@/components/Sidebar';
import Overview from '@/components/dashboard/Overview';
import Upgrades from '@/components/dashboard/Upgrades';
import Results from '@/components/dashboard/Results';
import Cars from '@/components/dashboard/Cars';
import Sponsors from '@/components/dashboard/Sponsors';
import Balances from '@/components/dashboard/Balances';
import { useState } from 'react';

// Definido fuera del componente: array estático, no se recrea en cada render
const SIDEBAR_ITEMS = [
    { key: 'overview',  label: 'Resumen'    },
    { key: 'upgrades',  label: 'Mejoras'    },
    { key: 'results',   label: 'Resultados' },
    { key: 'cars',      label: 'Coches'     },
    { key: 'sponsors',  label: 'Sponsors'   },
    { key: 'balances',  label: 'Balances'   },
];

// Mapa key → componente: O(1), sin if/switch
const SECTION_MAP = {
    overview: Overview,
    upgrades: Upgrades,
    results:  Results,
    cars:     Cars,
    sponsors: Sponsors,
    balances: Balances,
};

export default function Dashboard() {
    const { user } = useAuth();
    const [selectedSection, setSelectedSection] = useState(SIDEBAR_ITEMS[0].key);

    const SectionComponent = SECTION_MAP[selectedSection] ?? Overview;

    return (
        <AuthenticatedLayout>
            <div className="flex min-h-[70vh]">
                <Sidebar items={SIDEBAR_ITEMS} selected={selectedSection} onSelect={setSelectedSection} />

                <main className="flex-1 p-6">
                    <SectionComponent />
                </main>
            </div>
        </AuthenticatedLayout>
    );
}
