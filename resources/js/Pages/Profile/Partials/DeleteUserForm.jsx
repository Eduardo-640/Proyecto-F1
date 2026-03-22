import DangerButton from '@/Components/default/DangerButton';
import InputError from '@/Components/default/InputError';
import InputLabel from '@/Components/default/InputLabel';
import Modal from '@/Components/default/Modal';
import SecondaryButton from '@/Components/default/SecondaryButton';
import TextInput from '@/Components/default/TextInput';
import { useAuth } from '../../../context/AuthContext';
import { api } from '../../../api';
import React, { useRef, useState } from 'react';

export default function DeleteUserForm({ className = '' }) {
    const { logout } = useAuth();
    const [confirmingUserDeletion, setConfirmingUserDeletion] = useState(false);
    const [password, setPassword] = useState('');
    const [errors, setErrors] = useState({});
    const [processing, setProcessing] = useState(false);
    const passwordInput = useRef();

    const confirmUserDeletion = () => setConfirmingUserDeletion(true);

    const deleteUser = async (e) => {
        e.preventDefault();
        setProcessing(true);
        setErrors({});
        try {
            await api.delete('/api/auth/profile/');
            logout();
        } catch (err) {
            setErrors(err?.data?.errors ?? { password: err?.data?.detail ?? 'Error al eliminar la cuenta' });
            passwordInput.current?.focus();
        } finally {
            setProcessing(false);
        }
    };

    const closeModal = () => {
        setConfirmingUserDeletion(false);
        setErrors({});
        setPassword('');
    };

    return (
        <section className={`space-y-6 ${className}`}>
            <header>
                <h2 className="text-lg font-medium text-gray-900">
                    Delete Account
                </h2>

                <p className="mt-1 text-sm text-gray-600">
                    Once your account is deleted, all of its resources and data
                    will be permanently deleted. Before deleting your account,
                    please download any data or information that you wish to
                    retain.
                </p>
            </header>

            <DangerButton onClick={confirmUserDeletion}>
                Delete Account
            </DangerButton>

            <Modal show={confirmingUserDeletion} onClose={closeModal}>
                <form onSubmit={deleteUser} className="p-6">
                    <h2 className="text-lg font-medium text-gray-900">
                        Are you sure you want to delete your account?
                    </h2>

                    <p className="mt-1 text-sm text-gray-600">
                        Once your account is deleted, all of its resources and
                        data will be permanently deleted. Please enter your
                        password to confirm you would like to permanently delete
                        your account.
                    </p>

                    <div className="mt-6">
                        <InputLabel
                            htmlFor="password"
                            value="Password"
                            className="sr-only"
                        />

                        <TextInput
                            id="password"
                            type="password"
                            name="password"
                            ref={passwordInput}
                            value={data.password}
                            onChange={(e) =>
                                setData('password', e.target.value)
                            }
                            className="mt-1 block w-3/4"
                            isFocused
                            placeholder="Password"
                        />

                        <InputError
                            message={errors.password}
                            className="mt-2"
                        />
                    </div>

                    <div className="mt-6 flex justify-end">
                        <SecondaryButton onClick={closeModal}>
                            Cancel
                        </SecondaryButton>

                        <DangerButton className="ms-3" disabled={processing}>
                            Delete Account
                        </DangerButton>
                    </div>
                </form>
            </Modal>
        </section>
    );
}
