"""
High-level service layer for car setup snapshots.

This module sits between the views / management commands and the pure
algorithm in ``setup_generator.py``.  It handles:

* Generating the initial randomised preset for a driver's car.
* Applying sponsor-based starting department bonuses.
* Evolving the setup when a ``PurchasedUpgrade`` is applied.
* Generating per-circuit race-weekend setups (tunable params + BOP).
* Querying snapshot history.

Typical flow
------------
1. Season starts:
   a. ``apply_starting_bonuses(dev)``         — +1 level from sponsor affinity.
   b. ``generate_initial_preset(dev)``        — v1 snapshot with random bias.
2. Race weekend:
   ``generate_circuit_setup(dev, circuit, overrides, bop)``
3. Player buys an upgrade → ``apply_upgrade_to_setup(dev, upgrade)``.
4. Any time: ``get_latest_snapshot(team, season)`` → write to disk.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from . import setup_generator as sg
from .constants import AFFINITY_DEPARTMENT, PAYOUT_CONDITION_BOOST, Department
from .constants import UPGRADE_COST_BY_LEVEL
from .models import (
    BalanceOfPerformance,
    CarSetupSnapshot,
    CircuitEmphasis,
    CircuitSetup,
    PurchasedUpgrade,
    TeamDevelopment,
)

if TYPE_CHECKING:
    from apps.races.models import Circuit
    from apps.seasons.models import Season
    from apps.teams.models import Team


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _next_version(team: "Team", season: "Season") -> int:
    last = (
        CarSetupSnapshot.objects.filter(team=team, season=season)
        .order_by("-version")
        .values_list("version", flat=True)
        .first()
    )
    return (last + 1) if last is not None else 1


def _initial_bias(team: "Team", season: "Season") -> str:
    """Return the preset_bias stored in version 1 for this team+season."""
    return (
        CarSetupSnapshot.objects.filter(team=team, season=season)
        .order_by("version")
        .values_list("preset_bias", flat=True)
        .first()
        or ""
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_initial_preset(
    dev: TeamDevelopment,
    bias: str | None = None,
    circuit_key: str | None = None,
) -> CarSetupSnapshot:
    """Create version-1 ``CarSetupSnapshot`` for a team in a season.

    Parameters
    ----------
    dev:
        The ``TeamDevelopment`` instance (all fields already at their
        starting levels, typically 1).
    bias:
        One of the keys in ``setup_generator.PRESET_BIASES``.
        If *None* a random bias is chosen automatically.
    circuit_key:
        Optional circuit emphasis applied on top of everything else.

    Raises
    ------
    ValueError
        If a snapshot already exists for this team+season or if *bias*
        is not a recognised key.
    """
    if CarSetupSnapshot.objects.filter(team=dev.team, season=dev.season).exists():
        raise ValueError(
            f"A setup snapshot already exists for {dev.team} in {dev.season}. "
            "Use apply_upgrade_to_setup() to evolve the existing setup."
        )

    if bias is None:
        bias = random.choice(list(sg.PRESET_BIASES.keys()))
    elif bias not in sg.PRESET_BIASES:
        raise ValueError(
            f"Unknown preset bias '{bias}'. "
            f"Valid options: {sorted(sg.PRESET_BIASES)}"
        )

    params = sg.generate_setup_params(dev, circuit_key=circuit_key, preset_bias=bias)
    ini_content = sg.render_setup_ini(dev, circuit_key=circuit_key, preset_bias=bias)

    return CarSetupSnapshot.objects.create(
        team=dev.team,
        season=dev.season,
        version=1,
        ini_content=ini_content,
        params_json=params,
        changed_params={},  # no previous version to diff against
        upgrade=None,
        preset_bias=bias,
    )


def apply_upgrade_to_setup(
    dev: TeamDevelopment,
    upgrade: PurchasedUpgrade,
    circuit_key: str | None = None,
) -> CarSetupSnapshot | None:
    """Generate a new snapshot after an upgrade has been applied.

    The ``dev`` object must already reflect the new level (i.e. the
    upgrade has been saved to the DB before calling this function).
    The upgrade's ``applied`` flag should be ``True``.

    Returns the newly created ``CarSetupSnapshot``, or ``None`` if no
    INI parameter actually changed (e.g., the same level upgrade that
    does not cross any synergy threshold).

    Parameters
    ----------
    dev:
        The ``TeamDevelopment`` after the upgrade was applied.
    upgrade:
        The ``PurchasedUpgrade`` that triggered this evolution.
    circuit_key:
        Optional circuit emphasis for the generated setup.

    Raises
    ------
    ValueError
        If no initial snapshot exists yet for this team+season.
    """
    previous = (
        CarSetupSnapshot.objects.filter(team=dev.team, season=dev.season)
        .order_by("-version")
        .first()
    )
    if previous is None:
        raise ValueError(
            f"No setup snapshot found for {dev.team} in {dev.season}. "
            "Call generate_initial_preset() first."
        )

    # Carry forward the original personality
    bias = _initial_bias(dev.team, dev.season)

    new_params = sg.generate_setup_params(
        dev, circuit_key=circuit_key, preset_bias=bias or None
    )
    old_params: dict = previous.params_json

    changed = {k: v for k, v in new_params.items() if old_params.get(k) != v}

    if not changed:
        # No INI parameters were affected by this upgrade — skip snapshot.
        return None

    ini_content = sg.render_setup_ini(
        dev, circuit_key=circuit_key, preset_bias=bias or None
    )

    return CarSetupSnapshot.objects.create(
        team=dev.team,
        season=dev.season,
        version=previous.version + 1,
        ini_content=ini_content,
        params_json=new_params,
        changed_params=changed,
        upgrade=upgrade,
        preset_bias="",  # bias lives only on v1
    )


def get_latest_snapshot(team: "Team", season: "Season") -> CarSetupSnapshot | None:
    """Return the most recent snapshot for a team+season, or ``None``."""
    return (
        CarSetupSnapshot.objects.filter(team=team, season=season)
        .order_by("-version")
        .first()
    )


def compute_upgrade_cost(previous_level: int, new_level: int) -> int:
    """Compute cost for an upgrade from previous_level -> new_level.

    Currently only supports increments of +1. Returns the configured cost.
    """
    if new_level != previous_level + 1:
        raise ValueError("Only single-level upgrades are supported")
    return UPGRADE_COST_BY_LEVEL.get(previous_level, 0)


def get_snapshot_history(
    team: "Team", season: "Season"
) -> "django.db.models.QuerySet[CarSetupSnapshot]":
    """Return all snapshots for a team+season ordered oldest → newest."""
    return CarSetupSnapshot.objects.filter(team=team, season=season).order_by("version")


# ---------------------------------------------------------------------------
# Starting department bonus
# ---------------------------------------------------------------------------


def get_starting_department_bonus(team: "Team") -> dict[str, int]:
    """Return ``{department: +1}`` for departments boosted by the team's
    main sponsor affinities.

    Checks *all* affinity conditions of the main sponsor (if any) and maps
    each category to a department via ``AFFINITY_DEPARTMENT``.  The result
    is used to pre-level specific departments when season begins.

    Returns an empty dict if the team has no main sponsor or no affinity
    conditions that map to a department.
    """
    try:
        main_sponsor = team.sponsors.get(is_main=True, active=True)
    except team.sponsors.model.DoesNotExist:
        return {}
    except Exception:
        # sponsors relation may not exist in test environments
        return {}

    bonuses: dict[str, int] = {}
    # Accept sponsor conditions both of type affinity (positive) and penalty (negative).
    # For physical car departments, only allow a single-level (+1/-1) effect per department
    # coming from sponsor affinities/penalties. Economic effects (category 'money')
    # are handled separately by get_sponsor_money_multiplier().
    dept_values = {c.value for c in Department}
    for cond in main_sponsor.conditions.filter(type__in=("affinity", "penalty")):
        # try mapping affinity category to department first
        dept = AFFINITY_DEPARTMENT.get(cond.category)
        # fallback: if category already names a department, use it directly
        if not dept and cond.category in dept_values:
            dept = cond.category

        if not dept:
            # skip non-department categories here (e.g., points)
            continue

        # money handled elsewhere
        if cond.category == "money":
            continue

        # Normalize value to sign-only for department effects: +1, -1 or 0
        try:
            raw = int(cond.value)
        except Exception:
            raw = 0
        sign = 1 if raw > 0 else (-1 if raw < 0 else 0)

        if sign == 0:
            continue

        # Accumulate but clamp per department to [-1, +1]
        prev = bonuses.get(dept, 0)
        new = prev + sign
        # clamp
        if new > 1:
            new = 1
        if new < -1:
            new = -1
        bonuses[dept] = new

    # ── Synergy bonuses ────────────────────────────────────────────────────
    # If 2+ complementary departments are both boosted (+1), grant an extra
    # +1 to a third synergy department (capped so it never exceeds +1).
    SYNERGIES = [
        # (dept_a, dept_b) → synergy_dept  (thematic pairs)
        ("engine", "aerodynamics", "electronics"),  # speed package → data/power unit
        ("chassis", "suspension", "aerodynamics"),  # handling package → downforce
        ("engine", "electronics", "aerodynamics"),  # power unit → aero efficiency
        ("aerodynamics", "suspension", "chassis"),  # cornering → structural
    ]
    for dept_a, dept_b, synergy_dept in SYNERGIES:
        if bonuses.get(dept_a, 0) > 0 and bonuses.get(dept_b, 0) > 0:
            # Both parts of the pair are positively boosted: reward synergy dept
            if bonuses.get(synergy_dept, 0) < 1:
                bonuses[synergy_dept] = bonuses.get(synergy_dept, 0) + 1
                if bonuses[synergy_dept] > 1:
                    bonuses[synergy_dept] = 1
        elif bonuses.get(dept_a, 0) < 0 and bonuses.get(dept_b, 0) < 0:
            # Both penalised: compound the penalty on synergy dept
            if bonuses.get(synergy_dept, 0) > -1:
                bonuses[synergy_dept] = bonuses.get(synergy_dept, 0) - 1
                if bonuses[synergy_dept] < -1:
                    bonuses[synergy_dept] = -1

    return bonuses


def get_sponsor_money_multiplier(team: "Team") -> float:
    """Return a cost multiplier derived from the main sponsor's money affinity/penalty.

    Default is 1.0. Each unit of `value` on a `money` condition applies a 5%
    discount (positive) or surcharge (negative). Result is clamped to [0.5, 2.0].
    """
    try:
        main_sponsor = team.sponsors.get(is_main=True, active=True)
    except Exception:
        return 1.0

    total = 0
    for cond in main_sponsor.conditions.filter(category="money"):
        try:
            total += int(cond.value)
        except Exception:
            continue

    if total == 0:
        return 1.0

    multiplier = 1.0 - 0.05 * total
    # clamp
    multiplier = max(0.5, min(2.0, multiplier))
    return multiplier


def get_sponsor_department_multiplier(team: "Team", department: str) -> float:
    """Return a cost multiplier for a specific upgrade department based on sponsor conditions.

    Considers both direct department category names ('engine', 'chassis', …) and
    indirect mappings via AFFINITY_DEPARTMENT ('speed' → 'engine', etc.).

    affinity (+1) on the dept  →  5% discount  (× 0.95)
    penalty  (-1) on the dept  → 10% surcharge  (× 1.10)

    This gives department penalties real in-game weight during the season: if a sponsor
    is hostile to a department it will cost more to develop that dept, even though the
    starting-level floor (MIN_LEVEL=1) prevents the initial level from dropping below 1.

    Returns 1.0 if the team has no main sponsor or no relevant conditions.
    """
    try:
        main_sponsor = team.sponsors.get(is_main=True, active=True)
    except Exception:
        return 1.0

    dept_values = {c.value for c in Department}
    net = 0
    for cond in main_sponsor.conditions.filter(type__in=("affinity", "penalty")):
        # resolve which department this condition affects
        mapped = AFFINITY_DEPARTMENT.get(cond.category)
        if not mapped and cond.category in dept_values:
            mapped = cond.category
        if mapped != department:
            continue
        try:
            val = int(cond.value)
        except Exception:
            continue
        net += 1 if val > 0 else (-1 if val < 0 else 0)

    net = max(-1, min(1, net))
    if net > 0:
        return 0.95  # affinity → 5% discount
    if net < 0:
        return 1.10  # penalty → 10% surcharge
    return 1.0


def apply_starting_bonuses(dev: TeamDevelopment) -> dict[str, int]:
    """Apply sponsor-derived starting bonuses to an existing ``TeamDevelopment``.

    Idempotent: if ``dev.bonuses_applied`` is already True the function returns
    an empty dict without making any changes.

    Call this **once** after creating the season's ``TeamDevelopment`` row
    (before ``generate_initial_preset``).

    Returns the bonuses that were actually saved (empty if none or already applied).
    """
    # Always compute sponsor effects; even if `bonuses_applied` is True we may
    # need to apply pending negative/positive deltas that were missed earlier.
    bonuses = get_starting_department_bonus(dev.team)
    if not bonuses:
        return {}

    max_level = max(sg.LEVEL_PERF)
    min_level = 1
    fields_updated: list[str] = []
    applied_changes: dict[str, int] = {}
    for dept, delta in bonuses.items():
        current = dev.get_level(dept)
        new_level = max(min_level, min(current + delta, max_level))
        if new_level != current:
            setattr(dev, dept, new_level)
            fields_updated.append(dept)
            applied_changes[dept] = new_level - current

    if fields_updated:
        # Mark as applied if not already
        if not dev.bonuses_applied:
            dev.bonuses_applied = True
            fields_to_update = fields_updated + ["bonuses_applied", "updated_at"]
        else:
            fields_to_update = fields_updated + ["updated_at"]
        dev.save(update_fields=fields_to_update)

    # Return the actual delta applied per department (positive or negative)
    return applied_changes


# ---------------------------------------------------------------------------
# Circuit setup
# ---------------------------------------------------------------------------


def generate_circuit_setup(
    dev: TeamDevelopment,
    circuit: "Circuit",
    tunable_overrides: dict[str, int | float] | None = None,
) -> CircuitSetup:
    """Generate (or update) a race-weekend ``CircuitSetup`` for a team.

    Permanent parameters (SPRING_RATE, ROD_LENGTH) are taken directly from
    the current development level and **cannot** be overridden here.
    Tunable parameters (wings, dampers, diff, …) use the development-computed
    value as default but accept driver overrides within the level-unlocked
    bounds.

    BOP (ballast / restrictor) is fetched automatically from
    ``BalanceOfPerformance`` if a record exists for this team+season.
    The resulting INI has BOPsections appended at the end if applicable.

    Parameters
    ----------
    dev:
        Current ``TeamDevelopment`` for the team in this season.
    circuit:
        The ``Circuit`` model instance for the race weekend.
    tunable_overrides:
        ``{param_name: value}`` set by the driver.  Ignored for permanent
        params or values outside the valid range for the current level.

    Returns the saved ``CircuitSetup`` instance (created or updated).
    """
    # Derive the circuit_key for CIRCUIT_EMPHASIS fallback lookup
    circuit_key = circuit.name.lower().replace(" ", "_")

    # Carry forward the bias from the initial development snapshot
    bias = _initial_bias(dev.team, dev.season) or None

    # Load per-circuit emphasis from DB if available; fall back to hardcoded dict.
    try:
        emphasis_obj = CircuitEmphasis.objects.get(circuit=circuit)
        circuit_emphasis: dict[str, float] | None = emphasis_obj.as_dict()
    except CircuitEmphasis.DoesNotExist:
        circuit_emphasis = (
            None  # setup_generator will use CIRCUIT_EMPHASIS[circuit_key]
        )

    # Validate overrides: strip permanent params and clamp to level bounds
    validated_overrides: dict[str, int | float] = {}
    if tunable_overrides:
        bounds = sg.get_tunable_bounds(dev, preset_bias=bias)
        for param, value in tunable_overrides.items():
            if param not in sg.TUNABLE_PARAMS:
                continue  # silently drop permanent params
            if param not in sg.PARAM_MAP:
                continue  # unknown param — skip
            spec = sg.PARAM_MAP[param]
            lo, hi = bounds[param]
            clamped_val = max(lo, min(hi, value))
            validated_overrides[param] = (
                round(clamped_val) if spec.integer else clamped_val
            )

    # Fetch BOP: manual record wins; fall back to auto-computed from levels.
    auto_bop = sg.compute_bop(dev)
    try:
        bop = BalanceOfPerformance.objects.get(team=dev.team, season=dev.season)
        # Manual record explicitly set by admin — use it as-is.
        bop_dict = bop.as_bop_overrides
    except BalanceOfPerformance.DoesNotExist:
        # No manual record: derive BOP automatically from development levels.
        bop_dict = {}
        if auto_bop["ballast"] != 0:
            bop_dict["BALLAST"] = auto_bop["ballast"]
        if auto_bop["restrictor_pct"] > 0:
            bop_dict["RESTRICTOR"] = auto_bop["restrictor_pct"]

    ini_content = sg.render_setup_ini(
        dev,
        circuit_key=circuit_key,
        preset_bias=bias,
        tunable_overrides=validated_overrides,
        bop_overrides=bop_dict or None,
        circuit_emphasis=circuit_emphasis,
    )

    base_snapshot = get_latest_snapshot(dev.team, dev.season)

    setup, _ = CircuitSetup.objects.update_or_create(
        team=dev.team,
        season=dev.season,
        circuit=circuit,
        defaults={
            "base_snapshot": base_snapshot,
            "tunable_overrides": validated_overrides,
            "ini_content": ini_content,
        },
    )
    return setup
