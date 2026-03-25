import { Activity, AlertTriangle, Timer } from 'lucide-react';

const severityStyles = {
  info: 'bg-sky-500/10 text-sky-200 border-sky-500/30',
  warning: 'bg-amber-500/10 text-amber-200 border-amber-500/30',
  critical: 'bg-red-500/10 text-red-200 border-red-500/40',
};

export default function IncidentFeed({ incidents = [] }) {
  return (
    <section className="h-full rounded-3xl border border-white/5 bg-black/60 p-6">
      <div className="mb-4 flex items-center gap-2">
        <AlertTriangle size={18} className="text-amber-300" />
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/40">
            Incident Detection
          </p>
          <h3 className="text-lg font-semibold text-white">
            Eventos relevantes
          </h3>
        </div>
      </div>

      {incidents.length === 0 ? (
        <p className="text-sm text-white/50">
          No se registraron incidentes para esta carrera.
        </p>
      ) : (
        <ul className="space-y-4">
          {incidents.map((incident) => (
            <li
              key={incident.id ?? `${incident.lap}-${incident.type}`}
              className="rounded-2xl border border-white/5 bg-white/5 p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-white">
                    Vuelta {incident.lap ?? '—'}
                  </p>
                  <p className="mt-0.5 text-sm text-white/80">
                    {incident.driverName ?? '—'}
                  </p>
                </div>
                <span
                  className={`rounded-full border px-3 py-1 text-xs ${severityStyles[incident.severity ?? 'info']}`}
                >
                  {incident.type}
                </span>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-white/75">
                {incident.description}
              </p>
              <div className="mt-3 flex flex-wrap gap-3 text-xs text-white/60">
                {incident.impact && (
                  <span className="inline-flex items-center gap-1">
                    <Activity size={14} />
                    {incident.impact}
                  </span>
                )}
                {incident.timestamp && (
                  <span className="inline-flex items-center gap-1">
                    <Timer size={14} />
                    {incident.timestamp}
                  </span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
