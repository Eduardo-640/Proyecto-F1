import InputError from '@/components/ui/InputError';
import PrimaryButton from '@/components/ui/PrimaryButton';
import TextInput from '@/components/ui/TextInput';
import GuestLayout from '@/layouts/GuestLayout';
import React from 'react';
import { api } from '../../api';

export default function ForgotPassword({ status }) {
    const [email, setEmail] = React.useState('');
    const [errors, setErrors] = React.useState({});
    const [processing, setProcessing] = React.useState(false);
    const [sent, setSent] = React.useState(false);

    const submit = async (e) => {
        e.preventDefault();
        setProcessing(true);
        setErrors({});
        try {
            await api.post('/api/auth/password/reset-email/', { email });
            setSent(true);
        } catch (err) {
            setErrors({ email: err?.data?.detail ?? 'Error al enviar el correo' });
        } finally {
            setProcessing(false);
        }
    };

    return (
        <GuestLayout>
            <div className="mb-4 text-sm text-gray-600">
                ¿Olvidaste tu contraseña? Introduce tu email y te enviaremos un enlace de recuperación.
            </div>
            {(status || sent) && (
                <div className="mb-4 text-sm font-medium text-green-600">
                    {status ?? 'Enlace enviado. Revisa tu correo.'}
                </div>
            )}
            <form onSubmit={submit}>
                <TextInput id="email" type="email" name="email" value={email} className="mt-1 block w-full" isFocused={true} onChange={(e) => setEmail(e.target.value)} />
                <InputError message={errors.email} className="mt-2" />
                <div className="mt-4 flex items-center justify-end">
                    <PrimaryButton className="ms-4" disabled={processing}>Enviar enlace</PrimaryButton>
                </div>
            </form>
        </GuestLayout>
    );
}
