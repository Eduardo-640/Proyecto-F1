import UltimasNoticias from '../Components/default/UltimasNoticias';
import En_Directo from '../Components/secciones/SeccionEn_Directo';
import Proximas_carreras from '../Components/secciones/SeccionProximasCarreras';

export default function Home() {
    return (
        <div className="bg-black text-white">
            <En_Directo />
            <Proximas_carreras />
            {/*<UltimasNoticias />*/}
        </div>
    );
}
