/**
 * Thin API client for the Django REST backend.
 * Base URL can be overridden via VITE_API_BASE_URL env variable.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

function getCSRF() {
    return document.cookie
        .split('; ')
        .find((row) => row.startsWith('csrftoken='))
        ?.split('=')[1] ?? '';
}

async function request(method, path, body = null) {
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRF(),
    };

    const token = localStorage.getItem('access_token');
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${BASE_URL}${path}`, {
        method,
        headers,
        credentials: 'include',
        body: body ? JSON.stringify(body) : null,
    });

    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw Object.assign(new Error(err.detail ?? 'API error'), { status: res.status, data: err });
    }

    const text = await res.text();
    return text ? JSON.parse(text) : null;
}

export const api = {
    get:    (path)         => request('GET',    path),
    post:   (path, body)   => request('POST',   path, body),
    put:    (path, body)   => request('PUT',    path, body),
    patch:  (path, body)   => request('PATCH',  path, body),
    delete: (path)         => request('DELETE', path),
};
