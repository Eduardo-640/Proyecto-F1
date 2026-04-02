import { useEffect, useState } from "react";

export default function DriverRanking() {
    const [standings, setStandings] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchStandings = async () => {
            try {
                const response = await fetch("/api/public/standings/");
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                const data = await response.json();
                setStandings(data);
            } catch (error) {
                console.error("Error al cargar las calificaciones:", error);
                setError("No se pudieron cargar las calificaciones.");
            }
        };

        fetchStandings();
    }, []);

    return (
        <div className="bg-gray-800 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="bg-gray-900">
                            <th className="py-4 px-6 text-left">POS</th>
                            <th className="py-4 px-6 text-left">DRIVER</th>
                            <th className="py-4 px-6 text-left">COUNTRY</th>
                            <th className="py-4 px-6 text-left">TEAM</th>
                            <th className="py-4 px-6 text-right">POINTS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {error ? (
                            <tr>
                                <td colSpan="5" className="py-4 px-6 text-center text-red-500">
                                    {error}
                                </td>
                            </tr>
                        ) : (
                            standings.map((s) => (
                                <tr key={s.driver_id} className="border-t border-gray-700 hover:bg-gray-700">
                                    <td className="py-4 px-6">{s.position}</td>
                                    <td className="py-4 px-6 font-medium">{s.name} {s.last_name}</td>
                                    <td className="py-4 px-6">{s.country}</td>
                                    <td className="py-4 px-6">{s.team ?? "—"}</td>
                                    <td className="py-4 px-6 text-right font-bold">{s.points}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

