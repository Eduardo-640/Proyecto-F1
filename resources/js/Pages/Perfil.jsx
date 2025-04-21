import React from "react";
import { usePage } from "@inertiajs/react";

export default function Perfil() {
  const { auth } = usePage().props;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Perfil de Usuario</h1>
      <div className="bg-white shadow-md rounded-lg p-6">
        <div className="flex items-center mb-4">
          <img
            src={auth.user.profile_photo_url || "/images/default-profile.png"}
            alt="Foto de perfil"
            className="w-16 h-16 rounded-full mr-4"
          />
          <div>
            <h2 className="text-xl font-semibold">{auth.user.name}</h2>
            <p className="text-gray-600">{auth.user.email}</p>
          </div>
        </div>
        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2">Información adicional</h3>
          <p className="text-gray-700">Aquí puedes agregar más detalles sobre el usuario.</p>
        </div>
      </div>
    </div>
  );
}