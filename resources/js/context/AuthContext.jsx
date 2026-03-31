import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { api } from '../api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser]       = useState(undefined); // undefined = not yet checked
    const [loading, setLoading] = useState(true);

    const fetchUser = useCallback(async () => {
        try {
            const data = await api.get('/api/auth/me/');
            setUser(data);
        } catch {
            setUser(null);
        } finally {
            setLoading(false);
        }
    }, []);

    // ! Borrar este useEffect y llamar a fetchUser directamente desde Dashboard.jsx, para evitar llamadas innecesarias al backend desde páginas públicas como Home o Drivers
    useEffect(() => {
        // Evitar llamar a la validación del backend desde /dashboard
        try {
            const path = window?.location?.pathname ?? '';
            if (path === '/dashboard') {
                setLoading(false);
                return;
            }
        } catch (_) {
            // si window no está disponible, seguir con la validación
        }

        fetchUser();
    }, [fetchUser]);

    const login = useCallback(async (credentials) => {
        const data = await api.post('/api/auth/login/', credentials);
        if (data?.access) localStorage.setItem('access_token', data.access);
        if (data?.refresh) localStorage.setItem('refresh_token', data.refresh);
        await fetchUser();
        return data;
    }, [fetchUser]);

    const logout = useCallback(async () => {
        try { await api.post('/api/auth/logout/', {}); } catch { /* ignore */ }
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    }, []);

    return (
        <AuthContext.Provider value={{ user, loading, login, logout, refetch: fetchUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
    return ctx;
}
