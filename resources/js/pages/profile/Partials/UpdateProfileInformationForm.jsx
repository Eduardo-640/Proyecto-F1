import InputError from '@/components/ui/InputError';
import InputLabel from '@/components/ui/InputLabel';
import PrimaryButton from '@/components/ui/PrimaryButton';
import TextInput from '@/components/ui/TextInput';
import { Transition } from '@headlessui/react';
import React, { useState } from 'react';
import { useAuth } from '../../../context/AuthContext';
import { api } from '../../../api';

export default function UpdateProfileInformation({ mustVerifyEmail, status, className = '' }) {
    const { user, refetch } = useAuth();
    const [data, setData] = useState({ name: user?.name ?? '', email: user?.email ?? '' });
    const [errors, setErrors] = useState({});
    const [processing, setProcessing] = useState(false);
    const [saved, setSaved] = useState(false);
    const setField = (key, value) => setData((p) => ({ ...p, [key]: value }));

    const submit = async (e) => {
        e.preventDefault();
        setProcessing(true);
        setErrors({});
        try {
            await api.patch('/api/auth/profile/', data);
            await refetch();
            setSaved(true);
            setTimeout(() => setSaved(false), 2000);
        } catch (err) {
            setErrors(err?.data?.errors ?? {});
        } finally {
            setProcessing(false);
        }
    };

    return (
        <section className={className}>
            <header>
                <h2 className="text-lg font-medium text-gray-900">Información del perfil</h2>
                <p className="mt-1 text-sm text-gray-600">Actualiza el nombre y email de tu cuenta.</p>
            </header>
            <form onSubmit={submit} className="mt-6 space-y-6">
                <div>
                    <InputLabel htmlFor="name" value="Nombre" />
                    <TextInput id="name" className="mt-1 block w-full" value={data.name} onChange={(e) => setField('name', e.target.value)} required isFocused autoComplete="name" />
                    <InputError className="mt-2" message={errors.name} />
                </div>
                <div>
                    <InputLabel htmlFor="email" value="Email" />
                    <TextInput id="email" type="email" className="mt-1 block w-full" value={data.email} onChange={(e) => setField('email', e.target.value)} required autoComplete="username" />
                    <InputError className="mt-2" message={errors.email} />
                </div>
                <div className="flex items-center gap-4">
                    <PrimaryButton disabled={processing}>Guardar</PrimaryButton>
                    <Transition show={saved} enter="transition ease-in-out" enterFrom="opacity-0" leave="transition ease-in-out" leaveTo="opacity-0">
                        <p className="text-sm text-gray-600">Guardado.</p>
                    </Transition>
                </div>
            </form>
        </section>
    );
}
