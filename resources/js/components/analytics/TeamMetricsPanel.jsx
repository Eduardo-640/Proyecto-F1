import { Shield, TrendingUp } from 'lucide-react';

const progressColors = [
  'bg-red-500',
  'bg-orange-400',
  'bg-yellow-300',
  'bg-emerald-400',
  'bg-sky-400',
];

export default function TeamMetricsPanel({
  teams = [],
  activeTeamId,
  onSelectTeam,
  data,
  loading,
  error,
}) {
  return (
    <section className="rounded-3xl border border-white/5 bg-black/60 p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/40">
            Team Metrics
          </p>
          <h3 className="text-lg font-semibold text-white">
            Resumen de equipos
          </h3>
        </div>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {teams.map((team) => (
            <button
              key={team.teamId}
              type="button"
              onClick={() => onSelectTeam?.(team.teamId)}
              className={`whitespace-nowrap rounded-full border px-4 py-1.5 text-sm transition ${
                team.teamId === activeTeamId
                  ? 'border-emerald-400/70 bg-emerald-400/10 font-medium text-white'
                  : 'border-white/10 text-white/70 hover:border-white/30'
              }`}
            >
              {team.teamName}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <p className="mt-6 text-sm text-white/60">
          Cargando métricas del equipo...
        </p>
      )}
      {!loading && error && (
        <p className="mt-4 text-xs text-amber-300">{error}</p>
      )}

      {!loading && data && (
        <div className="mt-6 grid gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-[0.4em] text-white/40">
              Puntos
            </p>
            <p className="text-3xl font-semibold text-white">
              {data.totalPoints ?? '—'}
            </p>
            <p className="text-xs text-white/50">
              Suma piloto + bonificaciones
            </p>
          </div>
          <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-[0.4em] text-white/40">
              Créditos
            </p>
            <p className="text-3xl font-semibold text-white">
              {data.creditsGenerated ?? '—'}
            </p>
            <p className="text-xs text-white/50">Generados en la carrera</p>
          </div>
          <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
            <p className="text-xs uppercase tracking-[0.4em] text-white/40">
              Fiabilidad
            </p>
            <p className="text-3xl font-semibold text-white">
              {data.reliabilityScore ?? '—'}
            </p>
            <p className="text-xs text-white/50">Índice técnico</p>
          </div>
        </div>
      )}

      {!loading && data && (
        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center gap-2 text-sm text-white/60">
              <Shield size={18} />
              <span>Desarrollo técnico</span>
            </div>
            <ul className="mt-4 space-y-3">
              {Object.entries(data.development ?? {}).map(([dept, level]) => (
                <li key={dept}>
                  <div className="flex items-center justify-between text-sm text-white/70">
                    <span className="uppercase tracking-wide">{dept}</span>
                    <span>{level}/5</span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-white/10">
                    <div
                      className={`h-full rounded-full ${progressColors[(level ?? 1) - 1] ?? 'bg-white/40'}`}
                      style={{ width: `${((level ?? 0) / 5) * 100}%` }}
                    />
                  </div>
                </li>
              ))}
              {!Object.keys(data.development ?? {}).length && (
                <p className="text-sm text-white/50">
                  Sin datos de progreso técnico.
                </p>
              )}
            </ul>
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center gap-2 text-sm text-white/60">
              <TrendingUp size={18} />
              <span>Indicadores adicionales</span>
            </div>
            <ul className="mt-3 space-y-2 text-sm text-white/70">
              <li className="flex justify-between">
                <span>Promedio pit stop</span>
                <span>{data.pitStopAverage ?? '—'} s</span>
              </li>
              <li className="flex justify-between">
                <span>Podios</span>
                <span>{data.podiums ?? 0}</span>
              </li>
              {data.notes && (
                <li className="leading-relaxed text-white/60">{data.notes}</li>
              )}
            </ul>
          </div>
        </div>
      )}

      {!loading && !data && (
        <p className="mt-6 text-sm text-white/60">
          Selecciona un equipo para visualizar sus métricas.
        </p>
      )}
    </section>
  );
}
