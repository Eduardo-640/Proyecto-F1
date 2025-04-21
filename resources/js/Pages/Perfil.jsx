import { usePage, useForm } from "@inertiajs/react";

export default function Perfil() {
  const { auth, flash } = usePage().props;
  const { data, setData, put, processing, errors } = useForm({
    name: auth.user.name,
    email: auth.user.email,
    password: "",
    profile_photo: null,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    put(route("perfil.update"));
  };

  const handleFileChange = (e) => {
    setData("profile_photo", e.target.files[0]);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-start mb-4">
        <a
          href="/"
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md font_enlaces"
        >
          Volver al Inicio
        </a>
      </div>
      {flash?.success && (
        <div className="bg-green-500 text-white text-center py-2 rounded mb-4">
          {flash.success}
        </div>
      )}
      {Object.keys(errors).length > 0 && (
        <div className="bg-red-500 text-white text-center py-2 rounded mb-4">
          {Object.values(errors).join(" ")}
        </div>
      )}
      <h1 className="text-2xl font-bold mb-4 text-white">Perfil</h1>
      <form onSubmit={handleSubmit} className="bg-gray-800 shadow-md rounded-lg p-6">
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-medium text-gray-300">
            Nombre
          </label>
          <input
            type="text"
            id="name"
            value={data.name}
            onChange={(e) => setData("name", e.target.value)}
            className="mt-1 block w-full border-gray-600 bg-gray-700 text-white rounded-md shadow-sm focus:ring-red-500 focus:border-red-500 sm:text-sm"
          />
          {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
        </div>

        <div className="mb-4">
          <label htmlFor="email" className="block text-sm font-medium text-gray-300">
            Correo Electrónico
          </label>
          <input
            type="email"
            id="email"
            value={data.email}
            onChange={(e) => setData("email", e.target.value)}
            className="mt-1 block w-full border-gray-600 bg-gray-700 text-white rounded-md shadow-sm focus:ring-red-500 focus:border-red-500 sm:text-sm"
          />
          {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
        </div>

        <div className="mb-4">
          <label htmlFor="profile_photo" className="block text-sm font-medium text-gray-300">
            Foto de Perfil
          </label>
          <input
            type="file"
            id="profile_photo"
            onChange={handleFileChange}
            className="mt-1 block w-full text-gray-300 sm:text-sm"
          />
          {errors.profile_photo && <p className="text-red-500 text-sm mt-1">{errors.profile_photo}</p>}
        </div>

        <div className="mb-4">
          <label htmlFor="password" className="block text-sm font-medium text-gray-300">
            Contraseña
          </label>
          <input
            type="password"
            id="password"
            value={data.password}
            onChange={(e) => setData("password", e.target.value)}
            className="mt-1 block w-full border-gray-600 bg-gray-700 text-white rounded-md shadow-sm focus:ring-red-500 focus:border-red-500 sm:text-sm"
          />
          {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
        </div>

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={processing}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md"
          >
            Guardar Cambios
          </button>
        </div>
      </form>
    </div>
  );
}