import '../css/app.css';
import '../css/global.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap';

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './app';

const root = createRoot(document.getElementById('app'));
root.render(<App />);

