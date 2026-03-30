import { Activity, CornerUpRight, Gauge, Zap } from 'lucide-react';

function StatCard({ label, value, helper }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="truncate text-xs uppercase tracking-[0.25em] text-white/40">
        {label}
      </p>
      <p className="text-2xl font-semibold leading-tight text-white">
        {value ?? '—'}
      </p>
      {helper && <p className="mt-1 text-xs text-white/50">{helper}</p>}
    </div>
  );
}

export default function DriverMetricsPanel({
  drivers = [],
  activeDriverId,
  onSelectDriver,
  data,
  loading,
  error,
}) {
  const selectedDriver = drivers.find(
    (driver) => driver.driverId === activeDriverId,
  );

  return (
    <section className="rounded-3xl border border-white/5 bg-black/60 p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/40">
            Driver Metrics
          </p>
          <h3 className="text-lg font-semibold text-white">
            Telemetría individual
          </h3>
        </div>
        {selectedDriver && (
          <div className="text-sm text-white/60">
            {selectedDriver.driverName}
          </div>
        )}
      </div>

      <div className="mt-4 flex gap-2 overflow-x-auto pb-2">
        {drivers.map((driver) => (
          <button
            key={driver.driverId}
            type="button"
            onClick={() => onSelectDriver?.(driver.driverId)}
            className={`whitespace-nowrap rounded-2xl border px-4 py-2 text-sm transition ${
              driver.driverId === activeDriverId
                ? 'border-red-500/70 bg-red-500/10 font-medium text-white'
                : 'border-white/10 text-white/70 hover:border-white/30'
            }`}
          >
            {driver.driverCode ??
              String(driver.driverId ?? '')
                .substring(0, 3)
                .toUpperCase()}
          </button>
        ))}
      </div>

      {loading && (
        <div className="mt-8 text-sm text-white/60">
          Cargando métricas del piloto...
        </div>
      )}

      {!loading && error && (
        <p className="mt-4 text-xs text-amber-300">{error}</p>
      )}

      {!loading && data && (
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Mejor vuelta"
            value={data.bestLap ?? '—'}
            helper="Tiempo más rápido registrado"
          />
          <StatCard
            label="Consistencia"
            value={
              data.consistency != null
                ? `${Math.round(data.consistency <= 1 ? data.consistency * 100 : data.consistency)}%`
                : '—'
            }
            helper="Variación de ritmo"
          />
          <StatCard
            label="Posición media"
            value={data.averagePosition ?? '—'}
            helper="Promedio por vuelta"
          />
          <StatCard
            label="Adelantamientos"
            value={data.overtakes ?? 0}
            helper="Ganancias netas"
          />
        </div>
      )}

      {!loading && data && (
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center gap-2 text-sm text-white/60">
              <Gauge size={18} />
              <span>Pace index</span>
            </div>
            <p className="mt-2 text-4xl font-semibold text-white">
              {data.paceIndex ?? '—'}
            </p>
            {data.lapsLed != null && (
              <p className="text-xs text-white/50">
                Vueltas lideradas: {data.lapsLed}
              </p>
            )}
            {data.notes && (
              <p className="mt-3 text-sm leading-relaxed text-white/70">
                {data.notes}
              </p>
            )}
          </div>

          <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
            <div className="flex items-center gap-2 text-sm text-white/60">
              <Activity size={18} />
              <span>Stints y compuestos</span>
            </div>
            {data.tireStints?.length ? (
              <ul className="mt-3 space-y-2">
                {data.tireStints.map((stint, idx) => (
                  <li
                    key={`${stint.compound}-${idx}`}
                    className="flex items-center justify-between text-sm"
                  >
                    <div className="flex items-center gap-2 text-white">
                      <span className="inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/10">
                        <Zap size={16} className="text-amber-300" />
                      </span>
                      {stint.compound}
                    </div>
                    <span className="text-white/60">{stint.laps} vueltas</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-3 text-sm text-white/60">
                Sin información de neumáticos.
              </p>
            )}
          </div>
        </div>
      )}

      {!loading && !data && (
        <div className="mt-6 flex items-center gap-2 text-sm text-white/60">
          <CornerUpRight size={16} />
          Selecciona un piloto para ver sus métricas post-carrera.
        </div>
      )}
    </section>
  );
}
