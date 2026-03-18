"""
Car setup generation algorithm based on team's development levels.

Maps ``TeamDevelopment`` department levels (1–5) to Assetto Corsa .ini
setup parameters, applying:

* Non-linear performance curve  (level → modifier)
* Cross-department synergy bonuses
* Optional circuit-emphasis weights
* Fixed-parameter whitelist  (gears, fuel, tyres, … are never touched)

Public API
----------
compute_modifiers(dev, circuit_key=None) -> dict[str, float]
    Effective 0–1 modifier per department after synergies + circuit bias.

generate_setup_params(dev, circuit_key=None) -> dict[str, int|float]
    Raw INI value per parameter, ready to be written.

get_performance_rating(dev, circuit_key=None) -> float
    Single 0–100 score useful for race-result calculations.

render_setup_ini(dev, circuit_key=None, template_path=None) -> str
    Returns the full .ini content as a string (preserves template format).

write_setup_ini(dev, output_path, circuit_key=None, template_path=None)
    Writes the generated .ini file to *output_path*.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import TeamDevelopment

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEPARTMENTS = ("engine", "aerodynamics", "chassis", "suspension", "electronics")

#: Non-linear performance curve.  Level 1 = 40 %, level 5 = 100 %.
LEVEL_PERF: dict[int, float] = {
    1: 0.40,
    2: 0.55,
    3: 0.70,
    4: 0.85,
    5: 1.00,
}

#: Synergy rules: (dept_a, min_level_a, dept_b, min_level_b, bonus_fraction)
#: When both conditions are met each department receives +bonus to its modifier.
SYNERGY_RULES: list[tuple[str, int, str, int, float]] = [
    ("engine", 4, "chassis", 3, 0.05),  # power needs structural rigidity
    ("aerodynamics", 4, "suspension", 3, 0.05),  # downforce needs compliant suspension
    ("engine", 3, "electronics", 3, 0.05),  # power needs traction management
    ("chassis", 4, "suspension", 4, 0.08),  # rigid chassis + precise damping
]

#: Per-circuit department emphasis weights.
#: Multiplied over the base modifier; values > 1 reward the department more.
CIRCUIT_EMPHASIS: dict[str, dict[str, float]] = {
    "monza": {
        "engine": 1.20,
        "aerodynamics": 0.85,
        "chassis": 1.00,
        "suspension": 0.95,
        "electronics": 1.05,
    },
    "hungaroring": {
        "engine": 0.90,
        "aerodynamics": 1.20,
        "chassis": 1.05,
        "suspension": 1.10,
        "electronics": 1.00,
    },
    "silverstone": {
        "engine": 1.00,
        "aerodynamics": 1.10,
        "chassis": 1.15,
        "suspension": 1.00,
        "electronics": 0.95,
    },
    "imola": {
        "engine": 1.00,
        "aerodynamics": 1.05,
        "chassis": 1.05,
        "suspension": 1.20,
        "electronics": 1.00,
    },
    "spa": {
        "engine": 1.15,
        "aerodynamics": 1.05,
        "chassis": 1.00,
        "suspension": 1.05,
        "electronics": 1.00,
    },
    "barcelona": {
        "engine": 0.95,
        "aerodynamics": 1.10,
        "chassis": 1.10,
        "suspension": 1.00,
        "electronics": 1.05,
    },
}

#: Initial setup personalities.  Each key maps to per-department additive
#: offsets applied on top of the base LEVEL_PERF modifier.  They persist
#: across upgrades so a car always keeps its original character.
PRESET_BIASES: dict[str, dict[str, float]] = {
    # Straight-line focused — benefits engine-heavy circuits.
    "speed": {
        "engine": 0.12,
        "aerodynamics": -0.05,
        "chassis": 0.00,
        "suspension": -0.03,
        "electronics": 0.04,
    },
    # Maximum corner speed — strong in technical layouts.
    "cornering": {
        "engine": -0.04,
        "aerodynamics": 0.12,
        "chassis": 0.03,
        "suspension": 0.08,
        "electronics": 0.00,
    },
    # Tyre preservation and predictability over multiple stints.
    "consistency": {
        "engine": 0.00,
        "aerodynamics": 0.03,
        "chassis": 0.08,
        "suspension": 0.10,
        "electronics": 0.02,
    },
    # Differential and chassis precision — suits drivers who push late.
    "technical": {
        "engine": 0.02,
        "aerodynamics": 0.04,
        "chassis": 0.08,
        "suspension": 0.00,
        "electronics": 0.12,
    },
    # Brute straight-line power with some structural support.
    "raw_power": {
        "engine": 0.15,
        "aerodynamics": -0.06,
        "chassis": 0.05,
        "suspension": 0.00,
        "electronics": 0.00,
    },
    # Slight bonus everywhere — no single weakness, no peak strength.
    "balanced": {
        "engine": 0.04,
        "aerodynamics": 0.04,
        "chassis": 0.04,
        "suspension": 0.04,
        "electronics": 0.04,
    },
}

# ---------------------------------------------------------------------------
# Parameter specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParamSpec:
    """Describes how a single INI parameter maps to a department modifier."""

    department: str
    #: Value produced when modifier = 0.0  (effectively level 1, no synergy)
    min_val: float
    #: Value produced when modifier = 1.0  (effectively level 5, full synergy)
    max_val: float
    #: Whether to round the result to the nearest integer
    integer: bool = True
    #: True  → driver can override this value per circuit within level bounds.
    #: False → structural parameter; only changes when a development upgrade is applied.
    tunable: bool = False

    @property
    def inverted(self) -> bool:
        """True when a *lower* value represents better performance (e.g. PACKER_RANGE)."""
        return self.min_val > self.max_val


#: Maps each modifiable INI section name to its ParamSpec.
#: min_val → max_val direction matches "worse → better" development.
PARAM_MAP: dict[str, ParamSpec] = {
    # --- Engine ---
    # tunable: driver adjusts brake power / throttle response per circuit
    "BRAKE_POWER_MULT": ParamSpec("engine", 82, 99, True, tunable=True),
    # --- Aerodynamics ---
    # tunable: wing angle and ARB balance change every circuit
    "WING_0": ParamSpec("aerodynamics", 5, 18, True, tunable=True),
    "WING_1": ParamSpec("aerodynamics", 7, 22, True, tunable=True),
    "ARB_FRONT": ParamSpec("aerodynamics", 180_000, 380_000, True, tunable=True),
    "ARB_REAR": ParamSpec("aerodynamics", 40_000, 110_000, True, tunable=True),
    # --- Chassis (PERMANENT — structural, cannot change between races) ---
    "SPRING_RATE_LF": ParamSpec("chassis", 130, 230, True, tunable=False),
    "SPRING_RATE_RF": ParamSpec("chassis", 130, 230, True, tunable=False),
    "SPRING_RATE_LR": ParamSpec("chassis", 65, 130, True, tunable=False),
    "SPRING_RATE_RR": ParamSpec("chassis", 65, 130, True, tunable=False),
    "ROD_LENGTH_LF": ParamSpec("chassis", 45, 82, True, tunable=False),
    "ROD_LENGTH_RF": ParamSpec("chassis", 45, 82, True, tunable=False),
    "ROD_LENGTH_LR": ParamSpec("chassis", 150, 195, True, tunable=False),
    "ROD_LENGTH_RR": ParamSpec("chassis", 150, 195, True, tunable=False),
    # --- Suspension ---
    # tunable: circuit surface and kerb usage vary — dampers and packers adjust
    "DAMP_BUMP_LF": ParamSpec("suspension", 2, 9, True, tunable=True),
    "DAMP_BUMP_RF": ParamSpec("suspension", 2, 9, True, tunable=True),
    "DAMP_BUMP_LR": ParamSpec("suspension", 2, 8, True, tunable=True),
    "DAMP_BUMP_RR": ParamSpec("suspension", 2, 8, True, tunable=True),
    "DAMP_REBOUND_LF": ParamSpec("suspension", 2, 8, True, tunable=True),
    "DAMP_REBOUND_RF": ParamSpec("suspension", 2, 8, True, tunable=True),
    "DAMP_REBOUND_LR": ParamSpec("suspension", 1, 7, True, tunable=True),
    "DAMP_REBOUND_RR": ParamSpec("suspension", 1, 7, True, tunable=True),
    # Inverted: lower value = tighter/better; level unlocks the lower bound
    "PACKER_RANGE_LF": ParamSpec("suspension", 30, 12, True, tunable=True),
    "PACKER_RANGE_RF": ParamSpec("suspension", 30, 12, True, tunable=True),
    "PACKER_RANGE_LR": ParamSpec("suspension", 55, 28, True, tunable=True),
    "PACKER_RANGE_RR": ParamSpec("suspension", 55, 28, True, tunable=True),
    # --- Electronics ---
    # tunable: differential behaviour is driver preference
    "DIFF_POWER": ParamSpec("electronics", 12, 38, True, tunable=True),
    "DIFF_COAST": ParamSpec("electronics", 22, 52, True, tunable=True),
    "DIFF_PRELOAD": ParamSpec("electronics", 20, 52, True, tunable=True),
}

#: Convenience set of param names the driver is allowed to override per circuit.
TUNABLE_PARAMS: frozenset[str] = frozenset(k for k, v in PARAM_MAP.items() if v.tunable)

#: INI sections that must be copied verbatim from the template.
FIXED_PARAMS: frozenset[str] = frozenset(
    {
        "INTERNAL_GEAR_2",
        "INTERNAL_GEAR_3",
        "INTERNAL_GEAR_4",
        "INTERNAL_GEAR_5",
        "INTERNAL_GEAR_6",
        "INTERNAL_GEAR_7",
        "FUEL",
        "STEER_ASSIST",
        "TYRES",
        "CAR",
        "CAMBER_LF",
        "CAMBER_RF",
        "CAMBER_LR",
        "CAMBER_RR",
        "TOE_OUT_LF",
        "TOE_OUT_RF",
        "TOE_OUT_LR",
        "TOE_OUT_RR",
        "FRONT_BIAS",
        "PRESSURE_LF",
        "PRESSURE_RF",
        "PRESSURE_LR",
        "PRESSURE_RR",
        "__EXT_PATCH",
    }
)

DEFAULT_TEMPLATE: Path = (
    Path(__file__).parent / "templates" / "rss_formula_rss_3_v6_default.ini"
)

# ---------------------------------------------------------------------------
# Tunable bounds helper
# ---------------------------------------------------------------------------


def get_tunable_bounds(
    dev: "TeamDevelopment",
    preset_bias: str | None = None,
    circuit_emphasis: dict[str, float] | None = None,
) -> dict[str, tuple[int | float, int | float]]:
    """Return ``{param: (lo, hi)}`` for every tunable parameter.

    ``lo``/``hi`` represent the driver-selectable range for that circuit,
    constrained by the current development level:

    * Non-inverted (higher = better):  range = ``[spec.min_val, generated]``
    * Inverted (lower = better):       range = ``[generated, spec.min_val]``

    where *generated* is the value produced by ``generate_setup_params`` at
    the current level.  This means development *unlocks the ceiling*; the
    driver can always detune but never exceed what the car's level allows.
    """
    generated = generate_setup_params(
        dev, preset_bias=preset_bias, circuit_emphasis=circuit_emphasis
    )
    bounds: dict[str, tuple[int | float, int | float]] = {}
    for param, spec in PARAM_MAP.items():
        if not spec.tunable:
            continue
        gen_val = generated[param]
        if spec.inverted:
            # Lower is better; development unlocks a lower floor
            bounds[param] = (gen_val, spec.min_val)
        else:
            bounds[param] = (spec.min_val, gen_val)
    return bounds


# ---------------------------------------------------------------------------
# Core algorithm
# ---------------------------------------------------------------------------


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def compute_modifiers(
    dev: "TeamDevelopment",
    circuit_key: str | None = None,
    preset_bias: str | None = None,
    circuit_emphasis: dict[str, float] | None = None,
) -> dict[str, float]:
    """Return the effective performance modifier (0.0 – 1.10) per department.

    Pipeline:
    1. Convert each level to a base modifier via the non-linear ``LEVEL_PERF`` curve.
    2. Apply preset-bias offsets (the car's permanent personality).
    3. Add synergy bonuses where all conditions are satisfied.
    4. Optionally scale by circuit emphasis weights:
       * ``circuit_emphasis`` (explicit dict, e.g. from ``CircuitEmphasis.as_dict()``) takes priority.
       * Falls back to the hardcoded ``CIRCUIT_EMPHASIS[circuit_key]`` when ``circuit_emphasis`` is None.
    5. Clamp to ``[0.0, 1.10]``  (allows mild over-cap from synergies).
    """
    levels: dict[str, int] = {d: dev.get_level(d) for d in DEPARTMENTS}
    modifiers: dict[str, float] = {d: LEVEL_PERF[levels[d]] for d in DEPARTMENTS}

    if preset_bias and preset_bias in PRESET_BIASES:
        for dept, offset in PRESET_BIASES[preset_bias].items():
            if dept in modifiers:
                modifiers[dept] += offset

    for dept_a, min_a, dept_b, min_b, bonus in SYNERGY_RULES:
        if levels[dept_a] >= min_a and levels[dept_b] >= min_b:
            modifiers[dept_a] += bonus
            modifiers[dept_b] += bonus

    if circuit_key:
        emphasis = (
            circuit_emphasis
            if circuit_emphasis is not None
            else CIRCUIT_EMPHASIS.get(circuit_key.lower(), {})
        )
    else:
        emphasis = circuit_emphasis or {}
    for dept, weight in emphasis.items():
        if dept in modifiers:
            modifiers[dept] *= weight

    for dept in DEPARTMENTS:
        modifiers[dept] = _clamp(modifiers[dept], 0.0, 1.10)

    return modifiers


def generate_setup_params(
    dev: "TeamDevelopment",
    circuit_key: str | None = None,
    preset_bias: str | None = None,
    circuit_emphasis: dict[str, float] | None = None,
) -> dict[str, int | float]:
    """Return a mapping of INI section name → computed parameter value."""
    modifiers = compute_modifiers(dev, circuit_key, preset_bias, circuit_emphasis)
    params: dict[str, int | float] = {}

    for param, spec in PARAM_MAP.items():
        m = _clamp(modifiers[spec.department], 0.0, 1.0)
        raw = spec.min_val + m * (spec.max_val - spec.min_val)
        params[param] = round(raw) if spec.integer else raw

    return params


def get_performance_rating(
    dev: "TeamDevelopment",
    circuit_key: str | None = None,
    preset_bias: str | None = None,
    circuit_emphasis: dict[str, float] | None = None,
) -> float:
    """Return a single 0–100 performance score for the car."""
    modifiers = compute_modifiers(dev, circuit_key, preset_bias, circuit_emphasis)
    avg = sum(modifiers[d] for d in DEPARTMENTS) / len(DEPARTMENTS)
    return round(_clamp(avg * 100, 0.0, 100.0), 2)


# ---------------------------------------------------------------------------
# INI rendering
# ---------------------------------------------------------------------------


def render_setup_ini(
    dev: "TeamDevelopment",
    circuit_key: str | None = None,
    template_path: Path | None = None,
    preset_bias: str | None = None,
    tunable_overrides: dict[str, int | float] | None = None,
    bop_overrides: dict[str, int] | None = None,
    circuit_emphasis: dict[str, float] | None = None,
) -> str:
    """Parse the default template and overwrite computed parameters.

    The template is read line-by-line so the original formatting and
    parameter order are preserved exactly.  Only ``VALUE=`` lines inside
    sections listed in ``PARAM_MAP`` (and not in ``FIXED_PARAMS``) are
    replaced; everything else is copied verbatim.

    Parameters
    ----------
    tunable_overrides:
        Driver-set per-circuit values for params in ``TUNABLE_PARAMS``.
        Only accepted for params whose ``ParamSpec.tunable`` is ``True``;
        silently ignored otherwise.
    bop_overrides:
        Balance-of-Performance injections (e.g. ``{"BALLAST": 50,
        "RESTRICTOR": 10}``).  These sections are **appended** at the end
        of the INI if they don't already exist in the template.

    Returns the modified INI content as a string.
    """
    tpl = Path(template_path or DEFAULT_TEMPLATE)
    computed = generate_setup_params(dev, circuit_key, preset_bias, circuit_emphasis)

    # Apply validated driver overrides for tunable params
    if tunable_overrides:
        for param, value in tunable_overrides.items():
            if param in TUNABLE_PARAMS and param in computed:
                computed[param] = round(value) if PARAM_MAP[param].integer else value

    result: list[str] = []
    current_section: str | None = None
    template_sections: set[str] = set()

    for line in tpl.read_text(encoding="utf-8").splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            current_section = stripped[1:-1]
            template_sections.add(current_section)
            result.append(line)
        elif (
            current_section is not None
            and current_section in computed
            and current_section not in FIXED_PARAMS
            and stripped.startswith("VALUE=")
        ):
            result.append(f"VALUE={computed[current_section]}\n")
        else:
            result.append(line)

    # Append BOP sections not already present in the template
    if bop_overrides:
        for section, value in bop_overrides.items():
            if section not in template_sections:
                result.append(f"\n[{section}]\nVALUE={value}\n")

    return "".join(result)


def write_setup_ini(
    dev: "TeamDevelopment",
    output_path: str | Path,
    circuit_key: str | None = None,
    template_path: Path | None = None,
    preset_bias: str | None = None,
) -> None:
    """Write the generated setup INI to *output_path*.

    The parent directory is created if it does not exist.
    """
    content = render_setup_ini(dev, circuit_key, template_path, preset_bias)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
