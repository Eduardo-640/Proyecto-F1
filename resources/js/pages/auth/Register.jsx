import InputError from '@/components/ui/InputError';
import InputLabel from '@/components/ui/InputLabel';
import PrimaryButton from '@/components/ui/PrimaryButton';
import TextInput from '@/components/ui/TextInput';
import GuestLayout from '@/layouts/GuestLayout';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../../api';

export default function Register() {
    const navigate = useNavigate();
    const [data, setData] = useState({ name: '', email: '', password: '', password_confirmation: '' });
    const [errors, setErrors] = useState({});
    const [processing, setProcessing] = useState(false);
    const setField = (key, value) => setData((p) => ({ ...p, [key]: value }));

    const submit = async (e) => {
        e.preventDefault();
        setProcessing(true);
        setErrors({});
        try {
            await api.post('/api/auth/register/', data);
            navigate('/login');
        } catch (err) {
            setErrors(err?.data?.errors ?? { email: err?.data?.detail ?? 'Error al registrar' });
        } finally {
            setProcessing(false);
        }
    };

    return (
        <GuestLayout>
            <Head title="Register" />

            <form onSubmit={submit}>
                <div>
                    <InputLabel htmlFor="name" value="Nombre" />
                    <TextInput id="name" name="name" value={data.name} className="mt-1 block w-full" autoComplete="name" isFocused={true} onChange={(e) => setField('name', e.target.value)} required />
                    <InputError message={errors.name} className="mt-2" />
                </div>
                <div className="mt-4">
                    <InputLabel htmlFor="email" value="Email" />
                    <TextInput id="email" type="email" name="email" value={data.email} className="mt-1 block w-full" autoComplete="username" onChange={(e) => setField('email', e.target.value)} required />
                    <InputError message={errors.email} className="mt-2" />
                </div>
                <div className="mt-4">
                    <InputLabel htmlFor="password" value="Contraseña" />
                    <TextInput id="password" type="password" name="password" value={data.password} className="mt-1 block w-full" autoComplete="new-password" onChange={(e) => setField('password', e.target.value)} required />
                    <InputError message={errors.password} className="mt-2" />
                </div>
                <div className="mt-4">
                    <InputLabel htmlFor="password_confirmation" value="Confirmar contraseña" />
                    <TextInput id="password_confirmation" type="password" name="password_confirmation" value={data.password_confirmation} className="mt-1 block w-full" autoComplete="new-password" onChange={(e) => setField('password_confirmation', e.target.value)} required />
                    <InputError message={errors.password_confirmation} className="mt-2" />
                </div>
                <div className="mt-4 flex items-center justify-end">
                    <Link to="/login" className="rounded-md text-sm text-gray-600 underline hover:text-gray-900">
                        ¿Ya tienes cuenta?
                    </Link>
                    <PrimaryButton className="ms-4" disabled={processing}>Registrarse</PrimaryButton>
                </div>
            </form>
        </GuestLayout>
    );
}
