import InputError from '@/components/ui/InputError';
import InputLabel from '@/components/ui/InputLabel';
import PrimaryButton from '@/components/ui/PrimaryButton';
import TextInput from '@/components/ui/TextInput';
import GuestLayout from '@/layouts/GuestLayout';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

export default function Register() {
    const { register } = useAuth();
    const navigate = useNavigate();
    const [data, setData] = useState({
        steam_id: '',
        name: '',
        last_name: '',
        password: '',
        password_confirmation: '',
    });
    const [errors, setErrors] = useState({});
    const [processing, setProcessing] = useState(false);
    const setField = (key, value) => setData((p) => ({ ...p, [key]: value }));

    const submit = async (e) => {
        e.preventDefault();
        if (data.password !== data.password_confirmation) {
            setErrors({ password_confirmation: 'Las contraseñas no coinciden' });
            return;
        }
        setProcessing(true);
        setErrors({});
        try {
            await register({
                steam_id: data.steam_id,
                name: data.name,
                last_name: data.last_name,
                password: data.password,
                password_confirmation: data.password_confirmation,
            });
            navigate('/dashboard');
        } catch (err) {
            setErrors(err?.data?.errors ?? { steam_id: err?.data?.error ?? 'Error al registrar' });
        } finally {
            setProcessing(false);
        }
    };

    return (
        <GuestLayout>
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
                        required
                    />
                    <InputError message={errors.steam_id} className="mt-2 text-red-500 text-sm" />
                </div>

                <div className="mb-6">
                    <InputLabel htmlFor="name" value="Nombre" className="text-white" />
                    <TextInput
                        id="name"
                        type="text"
                        name="name"
                        value={data.name}
                        className="mt-1 block w-full rounded-lg border-gray-700 bg-gray-900 py-2 px-3 text-white"
                        autoComplete="given-name"
                        onChange={(e) => setField('name', e.target.value)}
                        required
                    />
                    <InputError message={errors.name} className="mt-2 text-red-500 text-sm" />
                </div>

                <div className="mb-6">
                    <InputLabel htmlFor="last_name" value="Apellido" className="text-white" />
                    <TextInput
                        id="last_name"
                        type="text"
                        name="last_name"
                        value={data.last_name}
                        className="mt-1 block w-full rounded-lg border-gray-700 bg-gray-900 py-2 px-3 text-white"
                        autoComplete="family-name"
                        onChange={(e) => setField('last_name', e.target.value)}
                    />
                    <InputError message={errors.last_name} className="mt-2 text-red-500 text-sm" />
                </div>

                <div className="mb-6">
                    <InputLabel htmlFor="password" value="Contraseña" className="text-white" />
                    <TextInput
                        id="password"
                        type="password"
                        name="password"
                        value={data.password}
                        className="mt-1 block w-full rounded-lg border-gray-700 bg-gray-900 py-2 px-3 text-white"
                        autoComplete="new-password"
                        onChange={(e) => setField('password', e.target.value)}
                        required
                    />
                    <InputError message={errors.password} className="mt-2 text-red-500 text-sm" />
                </div>

                <div className="mb-6">
                    <InputLabel htmlFor="password_confirmation" value="Confirmar contraseña" className="text-white" />
                    <TextInput
                        id="password_confirmation"
                        type="password"
                        name="password_confirmation"
                        value={data.password_confirmation}
                        className="mt-1 block w-full rounded-lg border-gray-700 bg-gray-900 py-2 px-3 text-white"
                        autoComplete="new-password"
                        onChange={(e) => setField('password_confirmation', e.target.value)}
                        required
                    />
                    <InputError message={errors.password_confirmation} className="mt-2 text-red-500 text-sm" />
                </div>

                <div className="flex items-center justify-between">
                    <Link to="/login" className="text-sm text-blue-400 hover:underline">
                        ¿Ya tienes cuenta?
                    </Link>
                    <PrimaryButton
                        className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg"
                        disabled={processing}
                    >
                        Registrarse
                    </PrimaryButton>
                </div>
            </form>
        </GuestLayout>
    );
}
