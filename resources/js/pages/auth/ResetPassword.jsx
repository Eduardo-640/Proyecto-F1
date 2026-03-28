import InputError from '@/components/ui/InputError';
import InputLabel from '@/components/ui/InputLabel';
import PrimaryButton from '@/components/ui/PrimaryButton';
import TextInput from '@/components/ui/TextInput';
import GuestLayout from '@/layouts/GuestLayout';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/api';

export default function ResetPassword({ token, email }) {
    const navigate = useNavigate();
    const [data, setData] = useState({ token: token ?? '', email: email ?? '', password: '', password_confirmation: '' });
    const [errors, setErrors] = useState({});
    const [processing, setProcessing] = useState(false);
    const setField = (key, value) => setData((p) => ({ ...p, [key]: value }));

    const submit = async (e) => {
        e.preventDefault();
        setProcessing(true);
        setErrors({});
        try {
            await api.post('/api/auth/password/reset/', data);
            navigate('/login');
        } catch (err) {
            setErrors(err?.data?.errors ?? { password: err?.data?.detail ?? 'Error al restablecer contraseña' });
        } finally {
            setProcessing(false);
        }
    };

    return (
        <GuestLayout>
            <Head title="Reset Password" />

            <form onSubmit={submit}>
                <div>
                    <InputLabel htmlFor="email" value="Email" />
                    <TextInput id="email" type="email" name="email" value={data.email} className="mt-1 block w-full" autoComplete="username" onChange={(e) => setField('email', e.target.value)} />
                    <InputError message={errors.email} className="mt-2" />
                </div>
                <div className="mt-4">
                    <InputLabel htmlFor="password" value="Nueva contraseña" />
                    <TextInput id="password" type="password" name="password" value={data.password} className="mt-1 block w-full" autoComplete="new-password" isFocused={true} onChange={(e) => setField('password', e.target.value)} />
                    <InputError message={errors.password} className="mt-2" />
                </div>
                <div className="mt-4">
                    <InputLabel htmlFor="password_confirmation" value="Confirmar contraseña" />
                    <TextInput type="password" id="password_confirmation" name="password_confirmation" value={data.password_confirmation} className="mt-1 block w-full" autoComplete="new-password" onChange={(e) => setField('password_confirmation', e.target.value)} />
                    <InputError message={errors.password_confirmation} className="mt-2" />
                </div>
                <div className="mt-4 flex items-center justify-end">
                    <PrimaryButton className="ms-4" disabled={processing}>Restablecer contraseña</PrimaryButton>
                </div>
            </form>
        </GuestLayout>
    );
}
