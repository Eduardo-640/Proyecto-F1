import Checkbox from '@/components/ui/Checkbox';
import InputError from '@/components/ui/InputError';
import InputLabel from '@/components/ui/InputLabel';
import PrimaryButton from '@/components/ui/PrimaryButton';
import TextInput from '@/components/ui/TextInput';
import GuestLayout from '@/layouts/GuestLayout';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export default function Login({ status, canResetPassword }) {
    const { login } = useAuth();
    const navigate = useNavigate();
    const [data, setData] = useState({ steam_id: '', password: '', remember: false });
    const [errors, setErrors] = useState({});
    const [processing, setProcessing] = useState(false);

    const setField = (key, value) => setData((p) => ({ ...p, [key]: value }));

    const submit = async (e) => {
        e.preventDefault();
        setProcessing(true);
        setErrors({});
        try {
            await login({ steam_id: data.steam_id, password: data.password });
            navigate('/dashboard');
        } catch (err) {
            setErrors(err?.data?.errors ?? { steam_id: err?.data?.error ?? 'Credenciales inválidas' });
            setField('password', '');
        } finally {
            setProcessing(false);
        }
    };

    return (
        <GuestLayout>
            {status && (
                <div className="mb-4 text-sm font-medium text-green-600">{status}</div>
            )}

            <form onSubmit={submit} className="bg-gray-800 p-8 rounded-lg shadow-lg">
                <div className="mb-6">
                    <InputLabel htmlFor="steam_id" value="Steam ID" className="text-white" />
                    <TextInput
                        id="steam_id"
                        type="text"
                        name="steam_id"
                        value={data.steam_id}
                        className="mt-1 block w-full rounded-lg border-gray-700 bg-gray-900 py-2 px-3 text-white"
                        autoComplete="username"
                        isFocused={true}
                        onChange={(e) => setField('steam_id', e.target.value)}
                    />
                    <InputError message={errors.steam_id} className="mt-2 text-red-500 text-sm" />
                </div>

                <div className="mb-6">
                    <InputLabel htmlFor="password" value="Contraseña" className="text-white" />
                    <TextInput
                        id="password"
                        type="password"
                        name="password"
                        value={data.password}
                        className="mt-1 block w-full rounded-lg border-gray-700 bg-gray-900 py-2 px-3 text-white"
                        autoComplete="current-password"
                        onChange={(e) => setField('password', e.target.value)}
                    />
                    <InputError message={errors.password} className="mt-2 text-red-500 text-sm" />
                </div>

                <div className="flex items-center justify-between mb-6">
                    <label className="flex items-center text-white">
                        <Checkbox
                            name="remember"
                            checked={data.remember}
                            onChange={(e) => setField('remember', e.target.checked)}
                        />
                        <span className="ml-2 text-sm">Recuérdame</span>
                    </label>
                    {canResetPassword && (
                        <Link to="/forgot-password" className="text-sm text-blue-400 hover:underline">
                            ¿Olvidaste tu contraseña?
                        </Link>
                    )}
                </div>

                <PrimaryButton
                    className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg"
                    disabled={processing}
                >
                    Iniciar Sesión
                </PrimaryButton>

                <p className="mt-4 text-center text-sm text-gray-400">
                    ¿No tienes cuenta?{' '}
                    <Link to="/register" className="text-red-400 hover:underline">
                        Regístrate
                    </Link>
                </p>
            </form>
        </GuestLayout>
    );
}
