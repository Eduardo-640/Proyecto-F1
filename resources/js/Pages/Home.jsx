import UltimasNoticias from '../Components/UltimasNoticias';
import En_Directo from '../Components/En_Directo';
import Proximas_carreras from '../Components/Proximas_carreras';

export default function Home() {
    return (
        <div className="bg-black text-white">
            <En_Directo />
            <Proximas_carreras />
            {/*<UltimasNoticias />*/}
        </div>
    );
}
