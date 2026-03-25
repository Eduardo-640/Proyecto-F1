import { Clock } from 'lucide-react';
import { useMemo, useState } from 'react';

const typeColors = {
  start: 'from-emerald-500/60 to-emerald-500/20',
  pit: 'from-orange-500/60 to-orange-500/20',
  safety: 'from-yellow-400/60 to-yellow-400/20',
  penalty: 'from-red-500/60 to-red-500/20',
  record: 'from-sky-500/60 to-sky-500/20',
  battle: 'from-purple-500/60 to-purple-500/20',
  incident: 'from-amber-500/60 to-amber-500/20',
  finish: 'from-red-500/60 to-red-500/20',
};

const MAX_EVENTS = 3;

export default function RaceTimeline({ events = [] }) {
  const [expanded, setExpanded] = useState(false);
  const hasOverflow = events.length > MAX_EVENTS;
  const visibleEvents = useMemo(() => {
    if (!hasOverflow) return events;
    return expanded ? events : events.slice(0, MAX_EVENTS);
  }, [events, expanded, hasOverflow]);
  const hiddenCount = Math.max(events.length - visibleEvents.length, 0);

  return (
    <section className="rounded-3xl border border-white/5 bg-black/60 p-6">
      <div className="mb-4 flex items-center gap-2">
        <Clock size={18} className="text-white/70" />
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-white/40">
            Race Timeline
          </p>
          <h3 className="text-lg font-semibold text-white">
            Cronología de eventos
          </h3>
        </div>
      </div>

      {events.length === 0 ? (
        <p className="text-sm text-white/60">Sin eventos registrados.</p>
      ) : (
        <>
          <div className="relative pl-6">
            <span
              className="absolute bottom-1 left-[11px] top-1 w-px bg-white/10"
              aria-hidden
            />
            <ul className="space-y-6">
              {visibleEvents.map((event, index) => (
                <li
                  key={`${event.lap}-${event.title}-${index}`}
                  className="relative"
                >
                  <span
                    className={`absolute left-[-1.125rem] top-1.5 h-6 w-6 rounded-full bg-gradient-to-b ${
                      typeColors[event.type] ?? 'from-white/70 to-white/10'
                    } border border-white/30`}
                  />
                  <div className="rounded-2xl border border-white/5 bg-white/5 p-4">
                    <p className="text-xs uppercase tracking-widest text-white/40">
                      Vuelta {event.lap ?? '—'}
                    </p>
                    <p className="text-base font-semibold text-white">
                      {event.title}
                    </p>
                    <p className="mt-1 text-sm leading-relaxed text-white/70">
                      {event.detail}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          {hasOverflow && (
            <button
              type="button"
              onClick={() => setExpanded((prev) => !prev)}
              className="mt-6 w-full rounded-2xl border border-white/10 px-4 py-2 text-sm font-medium text-white/80 transition hover:border-white/40 hover:text-white"
            >
              {expanded
                ? 'Ver menos eventos'
                : `Ver toda la cronología (${events.length})`}
              {!expanded && hiddenCount > 0 && (
                <span className="ml-2 rounded-full bg-white/10 px-2 py-0.5 text-xs text-white/50">
                  +{hiddenCount}
                </span>
              )}
            </button>
          )}
        </>
      )}
    </section>
  );
}
