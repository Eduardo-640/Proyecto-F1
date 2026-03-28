import { useEffect, useMemo, useState } from 'react';
import DriverMetricsPanel from '@/components/analytics/DriverMetricsPanel';
import IncidentFeed from '@/components/analytics/IncidentFeed';
import PositionEvolutionChart from '@/components/analytics/PositionEvolutionChart';
import RaceOverview from '@/components/analytics/RaceOverview';
import RaceTimeline from '@/components/analytics/RaceTimeline';
import TeamMetricsPanel from '@/components/analytics/TeamMetricsPanel';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import { api } from '@/api';
import {
  MOCK_ANALYTICS_RACES,
  MOCK_DRIVER_METRICS,
  MOCK_RACE_METRICS,
  MOCK_RACE_TIMELINES,
  MOCK_TEAM_METRICS,
} from '@/data/mockAnalytics';

function normalizeRaceList(payload) {
  const raw = Array.isArray(payload) ? payload : (payload?.results ?? []);
  return raw
    .map((item, idx) => ({
      id: `${item.id ?? ''}`,
      name:
        item.nombre ??
        item.name ??
        item.race_name ??
        item.title ??
        (item.circuito
          ? `Ronda ${item.numero_ronda ?? idx + 1} · ${item.circuito}`
          : `Carrera ${idx + 1}`),
      circuit:
        item.circuito ??
        item.circuit ??
        item.circuit_name ??
        item.circuit?.name ??
        item.location ??
        '',
      country:
        item.country ?? item.circuit?.country ?? item.circuit?.location ?? '',
      date:
        item.fecha_carrera ??
        item.date ??
        item.race_date ??
        item.start_time ??
        null,
      laps: item.laps ?? item.total_laps ?? null,
      round: item.numero_ronda ?? item.round ?? item.round_number ?? idx + 1,
      season:
        item.temporada ??
        item.season ??
        item.season_year ??
        item.year ??
        new Date().getFullYear(),
    }))
    .filter((race) => race.id);
}

function normalizeRaceMetrics(payload) {
  if (!payload) return null;
  const classification =
    payload.overview ?? payload.classification ?? payload.results ?? [];
  const overview = classification
    .map((row, idx) => ({
      position: row.position ?? row.final_position ?? row.rank ?? idx + 1,
      driverId:
        row.driver_id ?? row.driverId ?? row.driver?.id ?? `driver-${idx}`,
      driverName:
        row.driverName ??
        row.driver_name ??
        row.driver?.full_name ??
        row.driver?.name ??
        row.driver ??
        `Piloto ${idx + 1}`,
      driverCode:
        row.driverCode ??
        row.driver_code ??
        row.driver?.code ??
        row.code ??
        null,
      teamId: row.team_id ?? row.teamId ?? row.team?.id ?? row.team ?? null,
      teamName:
        row.teamName ?? row.team_name ?? row.team?.name ?? row.team ?? 'Equipo',
      totalTime:
        row.totalTime ??
        row.total_time ??
        row.time_formatted ??
        row.time ??
        '—',
      gapToLeader:
        row.gap ??
        row.gapToLeader ??
        row.gap_to_leader ??
        (row.position === 1 ? '—' : ''),
      points: row.points ?? row.score ?? 0,
    }))
    .sort((a, b) => a.position - b.position);

  const positionEvolution = (
    payload.positionEvolution ??
    payload.position_evolution ??
    payload.laps ??
    []
  ).map((lap, idx) => ({
    lap: lap.lap ?? lap.lap_number ?? lap.number ?? idx + 1,
    positions: (lap.positions ?? lap.order ?? [])
      .map((pos, pIdx) => ({
        driverId:
          pos.driver_id ??
          pos.driverId ??
          pos.driver?.id ??
          pos.code ??
          `driver-${pIdx}`,
        driverName: pos.driver_name ?? pos.driver?.name ?? pos.driver ?? null,
        teamName: pos.team_name ?? pos.team ?? null,
        code: pos.driver_code ?? pos.code ?? pos.driver?.code ?? null,
        position: pos.position ?? pos.rank ?? pos.order ?? null,
      }))
      .filter((entry) => entry.driverId && entry.position != null),
  }));

  const incidents = (payload.incidents ?? payload.events ?? [])
    .map((incident, idx) => ({
      id: incident.id ?? incident.uuid ?? `incident-${idx}`,
      lap: incident.lap ?? incident.lap_number ?? incident.lapNumber ?? null,
      driverId:
        incident.driver_id ?? incident.driverId ?? incident.driver?.id ?? null,
      driverName:
        incident.driver_name ??
        incident.driver?.name ??
        incident.driver ??
        null,
      type: incident.type ?? incident.event_type ?? 'Evento',
      description:
        incident.description ?? incident.detail ?? incident.message ?? '',
      impact: incident.impact ?? incident.delta ?? '',
      severity: incident.severity ?? 'info',
      timestamp: incident.timestamp ?? incident.occurred_at ?? null,
    }))
    .filter((incident) => incident.lap != null || incident.description);

  const race = payload.race ?? payload.meta ?? null;
  return {
    race: race
      ? {
          id: race.id ?? race.slug ?? null,
          name: race.name ?? race.title ?? race.race_name ?? null,
          circuit:
            race.circuit ?? race.circuit_name ?? race.circuit?.name ?? null,
          country: race.country ?? race.circuit?.country ?? null,
          date: race.date ?? race.race_date ?? race.start_time ?? null,
          laps: race.laps ?? race.total_laps ?? null,
        }
      : null,
    overview,
    positionEvolution,
    incidents,
  };
}

function normalizeTimeline(payload) {
  const events = Array.isArray(payload)
    ? payload
    : (payload?.timeline ?? payload?.events ?? []);
  return events.map((event, idx) => ({
    lap: event.lap ?? event.lap_number ?? event.number ?? idx,
    title: event.title ?? event.short ?? event.type ?? 'Evento',
    detail: event.detail ?? event.description ?? '',
    type: event.type ?? 'event',
  }));
}

function normalizeDriverMetrics(payload, fallbackDriver) {
  if (!payload) return null;
  return {
    driverId:
      payload.driver_id ?? payload.driverId ?? fallbackDriver?.driverId ?? null,
    driverName:
      payload.driver_name ??
      payload.driver?.name ??
      fallbackDriver?.driverName ??
      'Piloto',
    bestLap: payload.best_lap ?? payload.bestLap ?? null,
    averagePosition:
      payload.average_position ??
      payload.avg_position ??
      payload.averagePosition ??
      null,
    consistency: payload.consistency ?? payload.stability ?? null,
    overtakes:
      payload.overtakes ??
      payload.overtake_count ??
      payload.overtakeCount ??
      null,
    lapsLed: payload.laps_led ?? payload.lapsLed ?? null,
    paceIndex: payload.pace_index ?? payload.paceIndex ?? null,
    tireStints: payload.tire_stints ?? payload.stints ?? [],
    notes: payload.notes ?? payload.summary ?? null,
  };
}

function normalizeTeamMetrics(payload, fallbackTeam) {
  if (!payload) return null;
  return {
    teamId: payload.team_id ?? payload.teamId ?? fallbackTeam?.teamId ?? null,
    teamName:
      payload.team_name ??
      payload.teamName ??
      payload.team?.name ??
      fallbackTeam?.teamName ??
      'Equipo',
    totalPoints:
      payload.total_points ?? payload.totalPoints ?? payload.points ?? null,
    creditsGenerated:
      payload.credits_generated ??
      payload.creditsGenerated ??
      payload.credits ??
      payload.revenue ??
      null,
    podiums:
      payload.podiums ?? payload.podium_count ?? payload.podiumCount ?? null,
    pitStopAverage:
      payload.pit_stop_average ??
      payload.pitStopAverage ??
      payload.avg_pit_time ??
      null,
    reliabilityScore:
      payload.reliability_score ??
      payload.reliabilityScore ??
      payload.reliability ??
      null,
    development: payload.development ?? payload.departments ?? {},
    notes: payload.notes ?? payload.summary ?? null,
  };
}

export default function Analytics() {
  const [races, setRaces] = useState([]);
  const [racesLoading, setRacesLoading] = useState(true);
  const [raceNotice, setRaceNotice] = useState('');
  const [selectedRaceId, setSelectedRaceId] = useState(null);

  const [metrics, setMetrics] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [metricsNotice, setMetricsNotice] = useState('');

  const [timeline, setTimeline] = useState([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [timelineNotice, setTimelineNotice] = useState('');

  const [selectedDriverId, setSelectedDriverId] = useState(null);
  const [driverMetrics, setDriverMetrics] = useState(null);
  const [driverLoading, setDriverLoading] = useState(false);
  const [driverNotice, setDriverNotice] = useState('');

  const [selectedTeamId, setSelectedTeamId] = useState(null);
  const [teamMetrics, setTeamMetrics] = useState(null);
  const [teamLoading, setTeamLoading] = useState(false);
  const [teamNotice, setTeamNotice] = useState('');

  useEffect(() => {
    let cancelled = false;
    setRacesLoading(true);
    (async () => {
      try {
        const response = await api.get('/api/carreras/');
        if (cancelled) return;
        const normalized = normalizeRaceList(response);
        if (!normalized.length) throw new Error('empty-races');
        setRaces(normalized);
        setRaceNotice('');
        setSelectedRaceId((prev) => prev ?? normalized[0]?.id ?? null);
      } catch (error) {
        if (cancelled) return;
        setRaces(MOCK_ANALYTICS_RACES);
        setRaceNotice(
          'No se pudo sincronizar el calendario; usando carreras de referencia.',
        );
        setSelectedRaceId(
          (prev) => prev ?? MOCK_ANALYTICS_RACES[0]?.id ?? null,
        );
      } finally {
        if (!cancelled) setRacesLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedRaceId) return;
    let cancelled = false;
    setMetricsLoading(true);
    setMetricsNotice('');
    (async () => {
      try {
        const response = await api.get(`/api/race/${selectedRaceId}/metrics`);
        if (cancelled) return;
        const normalized = normalizeRaceMetrics(response);
        if (!normalized) throw new Error('empty-metrics');
        setMetrics(normalized);
        setMetricsNotice('');
      } catch (error) {
        if (cancelled) return;
        const fallback = MOCK_RACE_METRICS[selectedRaceId] ?? null;
        setMetrics(fallback);
        setMetricsNotice(
          fallback
            ? 'Mostrando métricas derivadas de results.json de ejemplo mientras se expone el endpoint real.'
            : 'Sin datos de métricas para esta carrera.',
        );
      } finally {
        if (!cancelled) setMetricsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedRaceId]);

  useEffect(() => {
    if (!selectedRaceId) return;
    let cancelled = false;
    setTimelineLoading(true);
    setTimelineNotice('');
    (async () => {
      try {
        const response = await api.get(`/api/race/${selectedRaceId}/timeline`);
        if (cancelled) return;
        const normalized = normalizeTimeline(response);
        if (!normalized.length) throw new Error('empty-timeline');
        setTimeline(normalized);
        setTimelineNotice('');
      } catch (error) {
        if (cancelled) return;
        const fallback = MOCK_RACE_TIMELINES[selectedRaceId] ?? [];
        setTimeline(fallback);
        setTimelineNotice(
          fallback.length
            ? 'Cronología generada con datos de muestra.'
            : 'Sin eventos en la cronología.',
        );
      } finally {
        if (!cancelled) setTimelineLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedRaceId]);

  useEffect(() => {
    if (!metrics?.overview?.length) {
      setSelectedDriverId(null);
      setSelectedTeamId(null);
      return;
    }
    setSelectedDriverId(metrics.overview[0].driverId);
    const firstTeam = metrics.overview.find((entry) => entry.teamId);
    setSelectedTeamId(firstTeam?.teamId ?? null);
  }, [metrics]);

  useEffect(() => {
    if (!selectedDriverId || !selectedRaceId) {
      setDriverMetrics(null);
      return;
    }
    let cancelled = false;
    setDriverLoading(true);
    setDriverNotice('');
    (async () => {
      try {
        const response = await api.get(
          `/api/driver/${selectedDriverId}/stats?race=${selectedRaceId}`,
        );
        if (cancelled) return;
        const fallbackDriver = metrics?.overview?.find(
          (driver) => driver.driverId === selectedDriverId,
        );
        const normalized = normalizeDriverMetrics(response, fallbackDriver);
        if (!normalized) throw new Error('empty-driver');
        setDriverMetrics(normalized);
        setDriverNotice('');
      } catch (error) {
        if (cancelled) return;
        const fallback =
          MOCK_DRIVER_METRICS[selectedRaceId]?.[selectedDriverId] ?? null;
        setDriverMetrics(fallback);
        setDriverNotice(
          fallback
            ? 'Métricas de piloto mostradas desde los results.json de referencia.'
            : 'No hay métricas disponibles para este piloto.',
        );
      } finally {
        if (!cancelled) setDriverLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedDriverId, selectedRaceId, metrics?.overview]);

  useEffect(() => {
    if (!selectedTeamId || !selectedRaceId) {
      setTeamMetrics(null);
      return;
    }
    let cancelled = false;
    setTeamLoading(true);
    setTeamNotice('');
    (async () => {
      try {
        const response = await api.get(
          `/api/team/${selectedTeamId}/stats?race=${selectedRaceId}`,
        );
        if (cancelled) return;
        const fallbackTeam = metrics?.overview?.find(
          (entry) => entry.teamId === selectedTeamId,
        );
        const normalized = normalizeTeamMetrics(response, fallbackTeam);
        if (!normalized) throw new Error('empty-team');
        setTeamMetrics(normalized);
        setTeamNotice('');
      } catch (error) {
        if (cancelled) return;
        const fallback =
          MOCK_TEAM_METRICS[selectedRaceId]?.[selectedTeamId] ?? null;
        setTeamMetrics(fallback);
        setTeamNotice(
          fallback
            ? 'Datos de equipo obtenidos de una referencia local mientras se expone el endpoint.'
            : 'No hay métricas agregadas para este equipo.',
        );
      } finally {
        if (!cancelled) setTeamLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedTeamId, selectedRaceId, metrics?.overview]);

  const selectedRace = useMemo(() => {
    return (
      races.find((race) => race.id === selectedRaceId) ?? metrics?.race ?? null
    );
  }, [races, selectedRaceId, metrics]);

  const teamOptions = useMemo(() => {
    if (!metrics?.overview) return [];
    const seen = new Map();
    metrics.overview.forEach((entry) => {
      if (!entry.teamId || seen.has(entry.teamId)) return;
      seen.set(entry.teamId, {
        teamId: entry.teamId,
        teamName: entry.teamName,
      });
    });
    return Array.from(seen.values());
  }, [metrics]);

  const statusMessages = [raceNotice, metricsNotice].filter(Boolean);

  return (
    <div className="min-h-screen bg-[#05060a] text-white">
      <Navbar />
      <main className="pb-16 pt-20">
        <section className="mx-auto max-w-7xl space-y-10 px-4">
          <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-red-600/20 via-black/40 to-black/80 p-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-xs uppercase tracking-[0.5em] text-white/40">
                  Analytics Suite
                </p>
                <h1 className="text-3xl font-semibold">
                  Panel de métricas de carrera
                </h1>
                <p className="mt-2 max-w-2xl text-white/70">
                  Analiza resultados, evolución de posiciones, incidentes y
                  estadísticas avanzadas de pilotos y equipos generadas desde
                  los archivos{' '}
                  <code className="rounded bg-white/10 px-1">results.json</code>{' '}
                  de Assetto Corsa y la base de datos.
                </p>
              </div>
              <div className="flex flex-col gap-2 self-start">
                <label className="text-xs uppercase tracking-[0.4em] text-white/60">
                  Carrera
                </label>
                <select
                  className="rounded-2xl border border-white/10 bg-black/60 px-4 py-2 text-sm focus:border-red-500/60 focus:ring-0"
                  value={selectedRaceId ?? ''}
                  onChange={(event) => setSelectedRaceId(event.target.value)}
                  disabled={racesLoading}
                >
                  {(races.length ? races : MOCK_ANALYTICS_RACES).map((race) => (
                    <option key={race.id} value={race.id}>
                      {`${race.round ? `Ronda ${race.round} · ` : ''}${race.name}`}
                    </option>
                  ))}
                </select>
                {racesLoading && (
                  <p className="text-xs text-white/50">
                    Sincronizando calendario...
                  </p>
                )}
              </div>
            </div>
            {statusMessages.length > 0 && (
              <div className="mt-4 space-y-2">
                {statusMessages.map((message) => (
                  <p
                    key={message}
                    className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-xs text-amber-300"
                  >
                    {message}
                  </p>
                ))}
              </div>
            )}
          </div>

          {metricsLoading ? (
            <section className="animate-pulse rounded-3xl border border-white/5 bg-black/60 p-6">
              <div className="h-5 w-1/3 rounded bg-white/10" />
              <div className="mt-6 h-40 rounded-2xl bg-white/5" />
            </section>
          ) : (
            <RaceOverview
              race={selectedRace ?? metrics?.race}
              entries={metrics?.overview ?? []}
            />
          )}
          {metricsNotice && !metricsLoading && (
            <p className="text-xs text-amber-300">{metricsNotice}</p>
          )}

          <div className="grid gap-6 lg:grid-cols-3">
            <div className="lg:col-span-2">
              <PositionEvolutionChart
                data={metrics?.positionEvolution ?? []}
                activeDriverId={selectedDriverId}
                onDriverFocus={setSelectedDriverId}
              />
            </div>
            <IncidentFeed incidents={metrics?.incidents ?? []} />
          </div>

          {timelineLoading ? (
            <section className="rounded-3xl border border-white/5 bg-black/60 p-6">
              <p className="text-sm text-white/60">Cargando cronología...</p>
            </section>
          ) : (
            <RaceTimeline events={timeline} />
          )}
          {timelineNotice && !timelineLoading && (
            <p className="text-xs text-amber-300">{timelineNotice}</p>
          )}

          <div className="grid gap-6 lg:grid-cols-2">
            <DriverMetricsPanel
              drivers={metrics?.overview ?? []}
              activeDriverId={selectedDriverId}
              onSelectDriver={setSelectedDriverId}
              data={driverMetrics}
              loading={driverLoading}
              error={driverNotice}
            />
            <TeamMetricsPanel
              teams={teamOptions}
              activeTeamId={selectedTeamId}
              onSelectTeam={setSelectedTeamId}
              data={teamMetrics}
              loading={teamLoading}
              error={teamNotice}
            />
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
