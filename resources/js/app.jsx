import '../css/app.css';
import '../css/global.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap';

import { createRoot } from 'react-dom/client';

const pages = import.meta.glob('./Pages/**/*.jsx');

async function mountApp() {
    // Try to resolve a page based on the pathname; fallback to Home or Welcome.
    const path = window.location.pathname.replace(/^\/+|\/+$/g, '');
    const candidate = path
        ? path.split('/').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('/')
        : 'Home';

    let importer = pages[`./Pages/${candidate}.jsx`];
    if (!importer) {
        // try last segment
        const last = candidate.split('/').pop();
        importer = pages[`./Pages/${last}.jsx`];
    }
    if (!importer) {
        importer = pages['./Pages/Home.jsx'] || pages['./Pages/Welcome.jsx'];
    }

    const module = await importer();
    const Page = module.default || module;

    let mountEl = document.getElementById('app');
    if (!mountEl) {
        mountEl = document.createElement('div');
        mountEl.id = 'app';
        document.body.appendChild(mountEl);
    }

    const root = createRoot(mountEl);
    root.render(
        <div className="min-h-screen bg-black text-white">
            <Page />
        </div>
    );
}

mountApp();
