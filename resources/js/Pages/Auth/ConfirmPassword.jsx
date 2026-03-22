import InputError from '@/Components/default/InputError';
import InputLabel from '@/Components/default/InputLabel';
import PrimaryButton from '@/Components/default/PrimaryButton';
import TextInput from '@/Components/default/TextInput';
import GuestLayout from '@/Layouts/GuestLayout';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api';

export default function ConfirmPassword() {
    const navigate = useNavigate();
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState({});
    const [processing, setProcessing] = useState(false);

    const submit = async (e) => {
        e.preventDefault();
        setProcessing(true);
        setErrors({});
        try {
            await api.post('/api/auth/password/confirm/', { password });
            navigate(-1);
        } catch (err) {
            setErrors({ password: err?.data?.detail ?? 'Contraseña incorrecta' });
            setPassword('');
        } finally {
            setProcessing(false);
        }
    };

    return (
        <GuestLayout>
            <div className="mb-4 text-sm text-gray-600">
                Área segura. Por favor, confirma tu contraseña para continuar.
            </div>
            <form onSubmit={submit}>
                <div className="mt-4">
                    <InputLabel htmlFor="password" value="Contraseña" />
                    <TextInput id="password" type="password" name="password" value={password} className="mt-1 block w-full" isFocused={true} onChange={(e) => setPassword(e.target.value)} />
                    <InputError message={errors.password} className="mt-2" />
                </div>
                <div className="mt-4 flex items-center justify-end">
                    <PrimaryButton className="ms-4" disabled={processing}>Confirmar</PrimaryButton>
                </div>
            </form>
        </GuestLayout>
    );
}
