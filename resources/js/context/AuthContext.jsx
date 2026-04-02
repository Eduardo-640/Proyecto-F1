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

    useEffect(() => {
        // Skip API call if there's no token stored locally
        if (!localStorage.getItem('access_token')) {
            setUser(null);
            setLoading(false);
            return;
        }
        fetchUser();
    }, [fetchUser]);

    const _storeTokensAndFetch = useCallback(async (data) => {
        if (data?.access)  localStorage.setItem('access_token',  data.access);
        if (data?.refresh) localStorage.setItem('refresh_token', data.refresh);
        await fetchUser();
        return data;
    }, [fetchUser]);

    const login = useCallback(async (credentials) => {
        const data = await api.post('/api/auth/login/', credentials);
        console.log('Login response:', data);
        return _storeTokensAndFetch(data);
    }, [_storeTokensAndFetch]);

    const register = useCallback(async (payload) => {
        const data = await api.post('/api/auth/register/', payload);
        return _storeTokensAndFetch(data);
    }, [_storeTokensAndFetch]);

    const logout = useCallback(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    }, []);

    return (
        <AuthContext.Provider value={{ user, loading, login, register, logout, refetch: fetchUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
    return ctx;
}