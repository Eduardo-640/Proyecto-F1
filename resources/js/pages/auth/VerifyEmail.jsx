import React, { useState } from 'react';
import PrimaryButton from '@/components/ui/PrimaryButton';
import GuestLayout from '@/layouts/GuestLayout';
import { Link } from 'react-router-dom';
import { api } from '@/api';
import { useAuth } from '@/context/AuthContext';

export default function VerifyEmail({ status }) {
    const { logout } = useAuth();
    const [processing, setProcessing] = useState(false);
    const [sent, setSent] = useState(false);

    const submit = async (e) => {
        e.preventDefault();
        setProcessing(true);
        try {
            await api.post('/api/auth/email/verification-notification/', {});
            setSent(true);
        } finally {
            setProcessing(false);
        }
    };

    return (
        <GuestLayout>
            <div className="mb-4 text-sm text-gray-600">
                Gracias por registrarte. Por favor, verifica tu dirección de correo haciendo clic en el enlace que te enviamos.
            </div>
            {(status === 'verification-link-sent' || sent) && (
                <div className="mb-4 text-sm font-medium text-green-600">
                    Se ha enviado un nuevo enlace de verificación a tu correo.
                </div>
            )}
            <form onSubmit={submit}>
                <div className="mt-4 flex items-center justify-between">
                    <PrimaryButton disabled={processing}>Reenviar correo de verificación</PrimaryButton>
                    <button type="button" onClick={logout} className="rounded-md text-sm text-gray-600 underline hover:text-gray-900">
                        Cerrar sesión
                    </button>
                </div>
            </form>
        </GuestLayout>
    );
}
