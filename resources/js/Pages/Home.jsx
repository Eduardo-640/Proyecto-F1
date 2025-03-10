import { Link } from '@inertiajs/react';
import UltimasNoticias from '../Components/UltimasNoticias';

export default function Home() {
    return (
        <div className="container mt-4">
            <h1 className="text-center mb-4">Bienvenido a F1 App</h1>
            <p className="text-center">
                Aquí podrás encontrar las últimas noticias de la Fórmula 1, un foro para aficionados y mucho más.
            </p>
            <div className="text-center">
                <Link className="btn btn-primary me-3" to="/noticias">Últimas Noticias</Link>
                <Link className="btn btn-success" to="/foro">Ir al Foro</Link>
            </div>

            <UltimasNoticias />
        </div>
    );
}
