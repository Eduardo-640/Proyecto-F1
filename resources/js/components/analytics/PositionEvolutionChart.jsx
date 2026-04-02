import { useMemo } from 'react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

const palette = [
  '#ef4444',
  '#0ea5e9',
  '#f97316',
  '#a855f7',
  '#facc15',
  '#10b981',
  '#ec4899',
  '#22d3ee',
  '#f472b6',
  '#60a5fa',
];

export default function PositionEvolutionChart({
  data = [],
  activeDriverId,
  onDriverFocus,
}) {
  const drivers = useMemo(() => {
    const seen = new Map();
    data?.forEach((lap) => {
      lap?.positions?.forEach((pos) => {
        if (!pos) return;
        const id = pos.driverId ?? pos.code;
        if (!id || seen.has(id)) return;
        seen.set(id, {
          driverId: id,
          label: pos.code ?? id.slice(0, 3).toUpperCase(),
          name: pos.driverName ?? pos.driver ?? pos.code ?? id,
          teamName: pos.teamName ?? '',
        });
      });
    });
    return Array.from(seen.values());
  }, [data]);

  const chartSeries = useMemo(() => {
    return (data ?? []).map((lap, idx) => {
      const row = { lap: lap?.lap ?? idx + 1 };
      lap?.positions?.forEach((pos) => {
        if (!pos) return;
        const id = pos.driverId ?? pos.code;
        if (!id) return;
        row[id] = pos.position;
      });
      return row;
    });
  }, [data]);

  const maxPosition = useMemo(() => {
    let max = 0;
    data?.forEach((lap) => {
      lap?.positions?.forEach((pos) => {
        if (pos?.position && pos.position > max) max = pos.position;
      });
    });
    return max;
  }, [data]);

  if (!drivers.length || !chartSeries.length) {
    return (
      <section className="rounded-3xl border border-white/5 bg-black/60 p-6">
        <h3 className="mb-2 text-lg font-semibold text-white">
          Evolución de posiciones
        </h3>
        <p className="text-sm text-white/60">
          Sin datos de vuelta contra vuelta para esta carrera.
        </p>
      </section>
    );
  }

  const tooltipFormatter = (value, key) => {
    const driver = drivers.find((d) => d.driverId === key);
    return [`P${value}`, driver?.label ?? key];
  };

  return (
    <section className="rounded-3xl border border-white/5 bg-black/60 p-6">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/40">
            Position Evolution
          </p>
          <h3 className="text-lg font-semibold text-white">
            Vuelta vs Posición
          </h3>
        </div>
        <p className="text-sm text-white/50">
          Haz clic en un piloto para fijarlo en los detalles.
        </p>
      </div>

      <div className="mt-6 h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartSeries}
            margin={{ left: 0, right: 0, top: 10, bottom: 5 }}
          >
            <CartesianGrid stroke="#ffffff10" vertical={false} />
            <XAxis
              dataKey="lap"
              stroke="#ffffff60"
              tick={{ fill: '#ffffff60', fontSize: 12 }}
              tickLine={false}
            />
            <YAxis
              domain={[maxPosition, 1]}
              reversed
              allowDecimals={false}
              stroke="#ffffff60"
              tick={{ fill: '#ffffff60', fontSize: 12 }}
              tickLine={false}
              label={{
                value: 'Posición',
                angle: -90,
                position: 'insideLeft',
                fill: '#ffffff50',
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0a0a0f',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 12,
              }}
              labelFormatter={(lap) => `Vuelta ${lap}`}
              formatter={tooltipFormatter}
            />
            {drivers.map((driver, idx) => (
              <Line
                key={driver.driverId}
                type="monotone"
                dataKey={driver.driverId}
                name={driver.label}
                stroke={palette[idx % palette.length]}
                strokeWidth={driver.driverId === activeDriverId ? 3 : 1.5}
                strokeOpacity={
                  driver.driverId === activeDriverId || !activeDriverId
                    ? 0.95
                    : 0.3
                }
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-5 flex flex-wrap gap-3">
        {drivers.map((driver, idx) => {
          const isActive = driver.driverId === activeDriverId;
          return (
            <button
              key={driver.driverId}
              type="button"
              onClick={() => onDriverFocus?.(driver.driverId)}
              className={`rounded-full border px-3 py-1.5 text-sm transition ${
                isActive
                  ? 'border-red-500/70 bg-red-500/10 text-white'
                  : 'border-white/10 text-white/70 hover:border-white/30'
              }`}
            >
              <span
                className="mr-1 font-semibold"
                style={{ color: palette[idx % palette.length] }}
              >
                {driver.label}
              </span>
              {driver.name}
            </button>
          );
        })}
      </div>
    </section>
  );
}
