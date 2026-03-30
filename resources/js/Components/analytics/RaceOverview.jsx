import { Flag, MapPin } from 'lucide-react';

const podiumStyles = {
  1: 'bg-gradient-to-r from-red-600/80 via-orange-500/70 to-amber-400/60 text-white',
  2: 'bg-white/5',
  3: 'bg-white/5',
};

export default function RaceOverview({ race, entries = [] }) {
  if (!race && !entries.length) return null;

  const formattedDate = race?.date
    ? new Date(race.date).toLocaleString('es-ES', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : null;

  return (
    <section className="rounded-3xl border border-white/5 bg-black/60 p-6 shadow-2xl shadow-red-950/30">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/50">
            Race Overview
          </p>
          <h2 className="text-2xl font-semibold tracking-tight text-white">
            {race?.name ?? 'Carrera no especificada'}
          </h2>
          <div className="mt-2 flex flex-wrap gap-3 text-sm text-white/70">
            {race?.circuit && (
              <span className="inline-flex items-center gap-1">
                <MapPin size={16} className="text-red-400" />
                {race.circuit}
              </span>
            )}
            {race?.country && <span>{race.country}</span>}
            {formattedDate && <span>{formattedDate}</span>}
            {race?.laps && <span>{race.laps} vueltas</span>}
          </div>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-200">
          <Flag size={18} />
          Panel post-carrera
        </div>
      </div>

      <div className="mt-6 overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-wider text-white/60">
            <tr>
              <th className="py-2 pr-4 font-medium">Pos</th>
              <th className="py-2 pr-4 font-medium">Piloto</th>
              <th className="py-2 pr-4 font-medium">Equipo</th>
              <th className="py-2 pr-4 font-medium">Tiempo total</th>
              <th className="py-2 pr-4 font-medium">Gap</th>
              <th className="py-2 pr-4 text-right font-medium">Pts</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr
                key={`${entry.driverId}-${entry.position}`}
                className={`border-t border-white/5 ${podiumStyles[entry.position] ?? ''}`}
              >
                <td className="py-3 pr-4 font-semibold text-white/80">
                  {entry.position}
                </td>
                <td className="py-3 pr-4">
                  <div className="flex flex-col">
                    <span className="font-medium leading-tight text-white">
                      {entry.driverName}
                    </span>
                    <span className="text-xs text-white/50">
                      {entry.driverCode ?? entry.driverId}
                    </span>
                  </div>
                </td>
                <td className="py-3 pr-4 text-white/80">{entry.teamName}</td>
                <td className="py-3 pr-4 text-white/70">
                  {entry.totalTime ?? '—'}
                </td>
                <td className="py-3 pr-4 text-white/60">
                  {entry.gapToLeader ?? '—'}
                </td>
                <td className="py-3 text-right">
                  <span className="inline-flex min-w-[3rem] justify-end font-semibold text-red-200">
                    {entry.points ?? 0}
                  </span>
                </td>
              </tr>
            ))}
            {!entries.length && (
              <tr>
                <td colSpan={6} className="py-6 text-center text-white/40">
                  Sin resultados registrados para esta carrera.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
