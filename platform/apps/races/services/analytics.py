from __future__ import annotations

import math
from collections import defaultdict
from functools import lru_cache
from typing import Any, Dict, List

from django.db.models import Sum

from apps.developments.models import TeamDevelopment
from apps.races.constants import RaceStatus
from apps.races.models import (
    CreditTransaction,
    Race,
    RaceResult,
    RaceSessionSnapshot,
)


def build_race_metrics(race_id: int) -> dict[str, Any]:
    bundle = _load_race_bundle(race_id)
    if not bundle["results"]:
        raise RaceResult.DoesNotExist("No hay resultados registrados para esta carrera")

    overview = _build_overview(bundle)
    incidents = _build_incidents(bundle, overview)

    race = bundle["race"]
    snapshot = {
        "id": race.id,
        "name": _race_label(race),
        "circuit": race.circuit.name if race.circuit else None,
        "country": race.circuit.location if race.circuit else None,
        "date": race.race_date,
        "laps": bundle["race_laps"],
        "round": race.round_number,
        "season": race.season.year if race.season else None,
    }

    return {
        "race": snapshot,
        "overview": overview,
        "positionEvolution": bundle["position_snapshots"],
        "incidents": incidents,
    }


def build_race_timeline(race_id: int) -> List[dict[str, Any]]:
    bundle = _load_race_bundle(race_id)
    race = bundle["race"]
    timeline: List[dict[str, Any]] = [
        {
            "lap": 0,
            "title": "Salida",
            "detail": f"{race.circuit.name if race.circuit else 'Circuito desconocido'}",
            "type": "start",
        }
    ]

    for pit in sorted(bundle["pit_events"], key=lambda evt: evt["lap"]):
        timeline.append(
            {
                "lap": pit["lap"],
                "title": "Pit stop",
                "detail": f"{pit['driverName']} cambió de {pit['from']} a {pit['to']}",
                "type": "pit",
            }
        )

    for incident in _build_incidents(bundle, _build_overview(bundle)):
        if incident["type"].lower().startswith("abandono"):
            timeline.append(
                {
                    "lap": incident.get("lap") or 0,
                    "title": "Abandono",
                    "detail": incident["description"],
                    "type": "incident",
                }
            )
        elif incident["type"].lower().startswith("vuelta"):
            timeline.append(
                {
                    "lap": incident.get("lap") or 0,
                    "title": "Vuelta rápida",
                    "detail": incident["description"],
                    "type": "record",
                }
            )

    leader = bundle["results"][0].driver.name if bundle["results"] else ""
    final_lap = bundle["race_laps"] or (bundle["position_snapshots"][-1]["lap"] if bundle["position_snapshots"] else 0)
    timeline.append(
        {
            "lap": final_lap,
            "title": "Bandera a cuadros",
            "detail": f"Ganador: {leader}",
            "type": "finish",
        }
    )

    return sorted(timeline, key=lambda item: item["lap"])


def build_driver_stats(driver_id: int, race_id: int) -> dict[str, Any]:
    bundle = _load_race_bundle(race_id)
    result = next((rr for rr in bundle["results"] if rr.driver_id == driver_id), None)
    if result is None:
        raise RaceResult.DoesNotExist("El piloto no tiene registros para esta carrera")

    history = bundle["driver_histories"].get(driver_id, [])
    lap_times = bundle["driver_lap_times"].get(driver_id, [])
    best_lap_entry = bundle["best_laps"].get(driver_id)
    overall_best = bundle.get("overall_best_lap")
    pit_events = bundle["pit_events_by_driver"].get(driver_id, [])
    stints = bundle["driver_stints"].get(driver_id, [])

    average_position = (
        round(sum(entry["position"] for entry in history) / len(history), 2)
        if history
        else result.position
    )
    overtakes = _count_overtakes(history)
    consistency = _compute_consistency(lap_times)
    pace_index = _compute_pace_index(best_lap_entry, overall_best)
    laps_led = sum(1 for entry in history if entry["position"] == 1)

    notes = []
    if overtakes:
        notes.append(f"{overtakes} adelantamientos netos")
    if pit_events:
        notes.append(f"{len(pit_events)} paradas en boxes")
    if not notes:
        notes.append("Carrera estable sin eventos destacados")

    return {
        "driverId": driver_id,
        "bestLap": _format_millis(best_lap_entry["lap_time"]) if best_lap_entry else None,
        "averagePosition": average_position,
        "consistency": consistency,
        "overtakes": overtakes,
        "lapsLed": laps_led,
        "paceIndex": pace_index,
        "tireStints": stints,
        "pitStops": len(pit_events),
        "notes": ". ".join(notes),
    }


def build_team_stats(team_id: int, race_id: int) -> dict[str, Any]:
    bundle = _load_race_bundle(race_id)
    team_results = [rr for rr in bundle["results"] if rr.team_id == team_id]
    if not team_results:
        raise RaceResult.DoesNotExist("El equipo no tiene resultados para esta carrera")

    total_points = sum(rr.points_awarded for rr in team_results)
    credit_sum = (
        CreditTransaction.objects.filter(team_id=team_id, race=bundle["race"])
        .aggregate(total=Sum("amount"))
        .get("total")
        or 0
    )
    podiums = sum(1 for rr in team_results if rr.position and rr.position <= 3)
    finishes = sum(1 for rr in team_results if rr.finished_race)
    reliability = round((finishes / len(team_results)) * 100) if team_results else 0

    driver_ids = [rr.driver_id for rr in team_results]
    pit_counts = [len(bundle["pit_events_by_driver"].get(driver_id, [])) for driver_id in driver_ids]
    pit_average = round(sum(pit_counts) / len(pit_counts), 2) if pit_counts else 0

    race = bundle["race"]
    dev = TeamDevelopment.objects.filter(team_id=team_id, season=race.season).first()
    development = (
        {
            "engine": dev.engine,
            "aerodynamics": dev.aerodynamics,
            "chassis": dev.chassis,
            "suspension": dev.suspension,
            "electronics": dev.electronics,
        }
        if dev
        else {}
    )

    driver_names = ", ".join(rr.driver.name for rr in team_results)

    return {
        "teamId": team_id,
        "teamName": team_results[0].team.name if team_results[0].team else None,
        "totalPoints": total_points,
        "creditsGenerated": credit_sum,
        "podiums": podiums,
        "pitStopAverage": pit_average,
        "reliabilityScore": reliability,
        "development": development,
        "notes": f"Pilotos: {driver_names}",
    }


@lru_cache(maxsize=32)
def _load_race_bundle(race_id: int) -> dict[str, Any]:
    race = Race.objects.select_related("season", "circuit").get(pk=race_id)
    results = list(
        RaceResult.objects.filter(race=race)
        .select_related("driver", "team")
        .order_by("position")
    )

    driver_lookup = _build_driver_lookup(results)
    snapshot = (
        RaceSessionSnapshot.objects.filter(race=race, session_type=RaceStatus.RACE)
        .order_by("-processed_at")
        .first()
    )
    payload = snapshot.payload if snapshot else {}
    lap_events = _extract_lap_events(payload, driver_lookup)
    position_data = _process_lap_events(driver_lookup, lap_events)

    bundle = {
        "race": race,
        "results": results,
        "position_snapshots": position_data["snapshots"],
        "driver_histories": position_data["histories"],
        "pit_events": position_data["pit_events"],
        "pit_events_by_driver": position_data["pit_events_by_driver"],
        "best_laps": position_data["best_laps"],
        "overall_best_lap": position_data["overall_best"],
        "driver_lap_times": position_data["lap_times"],
        "driver_stints": position_data["stints"],
        "race_laps": payload.get("RaceLaps") or payload.get("raceLaps") or 0,
    }
    return bundle


def _build_driver_lookup(results: List[RaceResult]) -> dict[str, Any]:
    profiles: Dict[str, dict] = {}
    alias_map: Dict[str, str] = {}
    primary_by_driver: Dict[int, str] = {}

    for rr in results:
        driver = rr.driver
        profile = {
            "id": driver.id,
            "name": driver.name,
            "code": _driver_code(driver),
            "team": rr.team.name if rr.team else None,
        }

        identifiers = []
        if driver.steam_id:
            identifiers.append(_normalize_identifier(driver.steam_id))
        if driver.name:
            identifiers.append(_normalize_identifier(driver.name))
        if driver.last_name:
            identifiers.append(_normalize_identifier(f"{driver.name} {driver.last_name}"))

        identifiers = [identifier for identifier in identifiers if identifier]
        if not identifiers:
            identifiers = [f"driver-{driver.id}"]

        primary = identifiers[0]
        profiles[primary] = profile
        primary_by_driver[driver.id] = primary
        for identifier in identifiers:
            alias_map[identifier] = primary

    return {
        "profiles": profiles,
        "alias_map": alias_map,
        "primary": primary_by_driver,
    }


def _extract_lap_events(payload: dict[str, Any], lookup: dict[str, Any]) -> List[dict[str, Any]]:
    laps_raw = (payload or {}).get("Laps") or (payload or {}).get("laps") or []
    alias_map = lookup["alias_map"]
    events: List[dict[str, Any]] = []
    for entry in laps_raw:
        guid = entry.get("DriverGuid") or entry.get("Guid") or (entry.get("Driver") or {}).get("Guid")
        name = entry.get("DriverName") or (entry.get("Driver") or {}).get("Name")
        key = _normalize_identifier(guid) or _normalize_identifier(name)
        if not key or key not in alias_map:
            continue
        events.append(
            {
                "identifier": alias_map[key],
                "timestamp": _safe_int(entry.get("Timestamp")) or 0,
                "lap_time": _safe_int(entry.get("LapTime")),
                "tyre": (entry.get("Tyre") or entry.get("Compound") or "").strip(),
            }
        )
    events.sort(key=lambda item: item["timestamp"])
    return events


def _process_lap_events(lookup: dict[str, Any], lap_events: List[dict[str, Any]]) -> dict[str, Any]:
    primary = lookup["primary"]
    profiles = lookup["profiles"]
    driver_state: Dict[str, dict] = {}
    for driver_id, identifier in primary.items():
        profile = profiles.get(identifier)
        if not profile:
            continue
        driver_state[identifier] = {
            "driver_id": driver_id,
            "profile": profile,
            "laps": 0,
            "timestamp": 0,
            "current_tyre": None,
            "current_stint_laps": 0,
        }

    snapshots: List[dict[str, Any]] = []
    pit_events: List[dict[str, Any]] = []
    pit_events_by_driver: Dict[int, List[dict[str, Any]]] = defaultdict(list)
    best_laps: Dict[int, dict] = {}
    lap_times: Dict[int, List[int]] = defaultdict(list)
    stints: Dict[int, List[dict]] = defaultdict(list)
    last_published = 0

    for event in lap_events:
        identifier = event["identifier"]
        state = driver_state.get(identifier)
        if not state:
            continue
        state["laps"] += 1
        state["timestamp"] = event["timestamp"] or state["timestamp"]
        lap_number = state["laps"]
        driver_id = state["driver_id"]

        lap_time = event.get("lap_time")
        if lap_time and lap_time < 999999999:
            lap_times[driver_id].append(lap_time)
            best = best_laps.get(driver_id)
            if best is None or lap_time < best["lap_time"]:
                best_laps[driver_id] = {"lap_time": lap_time, "lap": lap_number}

        tyre = event.get("tyre") or state.get("current_tyre")
        if tyre:
            if state.get("current_tyre") is None:
                state["current_tyre"] = tyre
                state["current_stint_laps"] = 0
            elif tyre != state.get("current_tyre"):
                stints[driver_id].append(
                    {
                        "compound": state["current_tyre"],
                        "laps": state.get("current_stint_laps", 0),
                    }
                )
                pit_event = {
                    "driverId": driver_id,
                    "driverName": state["profile"]["name"],
                    "lap": lap_number,
                    "from": state["current_tyre"],
                    "to": tyre,
                }
                pit_events.append(pit_event)
                pit_events_by_driver[driver_id].append(pit_event)
                state["current_tyre"] = tyre
                state["current_stint_laps"] = 0
            state["current_stint_laps"] = state.get("current_stint_laps", 0) + 1

        current_max = max((info["laps"] for info in driver_state.values()), default=0)
        if current_max > last_published:
            ordered = sorted(
                driver_state.values(),
                key=lambda info: (-info["laps"], info["timestamp"], info["driver_id"]),
            )
            positions = []
            for idx, info in enumerate(ordered, start=1):
                profile = info["profile"]
                positions.append(
                    {
                        "driverId": profile["id"],
                        "driverName": profile["name"],
                        "code": profile["code"],
                        "teamName": profile["team"],
                        "position": idx,
                    }
                )
            snapshots.append({"lap": current_max, "positions": positions})
            last_published = current_max

    for state in driver_state.values():
        driver_id = state["driver_id"]
        tyre = state.get("current_tyre")
        stint_laps = state.get("current_stint_laps", 0)
        if tyre and stint_laps:
            stints[driver_id].append({"compound": tyre, "laps": stint_laps})

    histories_dict: Dict[int, List[dict]] = defaultdict(list)
    for snapshot in snapshots:
        lap_number = snapshot["lap"]
        for pos in snapshot["positions"]:
            histories_dict[pos["driverId"]].append({"lap": lap_number, "position": pos["position"]})

    histories = {driver_id: entries for driver_id, entries in histories_dict.items()}
    pit_events_by_driver = {driver_id: entries for driver_id, entries in pit_events_by_driver.items()}
    lap_times = {driver_id: entries for driver_id, entries in lap_times.items()}
    stints = {driver_id: entries for driver_id, entries in stints.items()}

    overall_best = None
    if best_laps:
        fastest_driver = min(best_laps.items(), key=lambda item: item[1]["lap_time"])
        overall_best = {"driverId": fastest_driver[0], **fastest_driver[1]}

    return {
        "snapshots": snapshots,
        "histories": histories,
        "pit_events": pit_events,
        "pit_events_by_driver": pit_events_by_driver,
        "best_laps": {driver_id: data for driver_id, data in best_laps.items()},
        "overall_best": overall_best,
        "lap_times": lap_times,
        "stints": stints,
    }


def _build_overview(bundle: dict[str, Any]) -> List[dict[str, Any]]:
    results = bundle["results"]
    if not results:
        return []
    leader_time = results[0].total_time or 0
    overview = []
    for rr in results:
        total_time = _format_millis(rr.total_time)
        gap = _format_gap(rr.total_time, leader_time)
        overview.append(
            {
                "position": rr.position,
                "driverId": rr.driver_id,
                "driverName": rr.driver.name,
                "driverCode": _driver_code(rr.driver),
                "teamId": rr.team_id,
                "teamName": rr.team.name if rr.team else None,
                "totalTime": total_time,
                "gapToLeader": gap if rr.position != 1 else "—",
                "points": rr.points_awarded,
                "finished": rr.finished_race,
            }
        )
    return overview


def _build_incidents(bundle: dict[str, Any], overview: List[dict[str, Any]]) -> List[dict[str, Any]]:
    incidents: List[dict[str, Any]] = []

    for entry in overview:
        if not entry.get("finished"):
            incidents.append(
                {
                    "id": f"dnf-{entry['driverId']}",
                    "lap": None,
                    "driverId": entry["driverId"],
                    "driverName": entry["driverName"],
                    "type": "Abandono (DNF)",
                    "description": f"{entry['driverName']} abandonó la carrera",
                    "impact": "Sin puntos",
                    "severity": "critical",
                }
            )

    histories = bundle["driver_histories"]
    for driver_id, history in histories.items():
        previous = None
        for item in history:
            if previous and item["position"] - previous["position"] >= 3:
                incidents.append(
                    {
                        "id": f"loss-{driver_id}-{item['lap']}",
                        "lap": item["lap"],
                        "driverId": driver_id,
                        "driverName": _driver_name(bundle, driver_id),
                        "type": "Pérdida de posiciones",
                        "description": f"Cayó de P{previous['position']} a P{item['position']}",
                        "impact": "Requiere análisis",
                        "severity": "warning",
                    }
                )
            previous = item

    for pit in bundle["pit_events"]:
        incidents.append(
            {
                "id": f"pit-{pit['driverId']}-{pit['lap']}",
                "lap": pit["lap"],
                "driverId": pit["driverId"],
                "driverName": pit["driverName"],
                "type": "Pit stop",
                "description": f"Cambio de {pit['from']} a {pit['to']}",
                "impact": "Estrategia",
                "severity": "info",
            }
        )

    fastest = bundle.get("overall_best_lap")
    if fastest:
        incidents.append(
            {
                "id": f"fast-{fastest['driverId']}",
                "lap": fastest.get("lap"),
                "driverId": fastest["driverId"],
                "driverName": _driver_name(bundle, fastest["driverId"]),
                "type": "Vuelta rápida",
                "description": f"{_driver_name(bundle, fastest['driverId'])} marcó {_format_millis(fastest['lap_time'])}",
                "impact": "+1 punto" if bundle["race"].status == RaceStatus.RACE else "",
                "severity": "info",
            }
        )

    return sorted(incidents, key=lambda item: (item.get("lap") or 0, item["id"]))


def _count_overtakes(history: List[dict[str, Any]]) -> int:
    overtakes = 0
    for previous, current in zip(history, history[1:]):
        if current["position"] < previous["position"]:
            overtakes += previous["position"] - current["position"]
    return overtakes


def _compute_consistency(lap_times: List[int]) -> float | None:
    if len(lap_times) < 2:
        return None
    avg = sum(lap_times) / len(lap_times)
    variance = sum((lap - avg) ** 2 for lap in lap_times) / len(lap_times)
    std_dev = math.sqrt(variance)
    consistency = max(0.0, 1 - (std_dev / avg))
    return round(consistency, 3)


def _compute_pace_index(best_lap: dict | None, overall_best: dict | None) -> int | None:
    if not best_lap or not overall_best:
        return None
    fastest = overall_best["lap_time"]
    if not fastest:
        return None
    delta = best_lap["lap_time"] - fastest
    pace = max(0, 100 - int((delta / fastest) * 100))
    return pace


def _driver_code(driver) -> str | None:
    if driver.number:
        return str(driver.number).zfill(2)
    if driver.name:
        parts = driver.name.split()
        return "".join(part[0] for part in parts[:3]).upper()
    return None


def _format_millis(value: int | None) -> str | None:
    if not value or value <= 0:
        return None
    seconds = value / 1000
    minutes = int(seconds // 60)
    remaining = seconds - (minutes * 60)
    return f"{minutes}:{remaining:06.3f}"


def _format_gap(value: int | None, leader_time: int) -> str | None:
    if not value or not leader_time or value <= 0 or leader_time <= 0:
        return None
    delta = (value - leader_time) / 1000
    if delta <= 0:
        return "+0.000"
    minutes = int(delta // 60)
    remaining = delta - (minutes * 60)
    if minutes:
        return f"+{minutes}:{remaining:06.3f}"
    return f"+{remaining:.3f}"


def _normalize_identifier(value: str | None) -> str | None:
    if not value:
        return None
    return value.strip().lower()


def _race_label(race: Race) -> str:
    circuit = race.circuit.name if race.circuit else "Carrera"
    year = race.season.year if race.season else ""
    return f"{circuit} {year}".strip()


def _driver_name(bundle: dict[str, Any], driver_id: int) -> str:
    for rr in bundle["results"]:
        if rr.driver_id == driver_id:
            return rr.driver.name
    return "Piloto"


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
