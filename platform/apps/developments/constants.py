from django.db import models

MIN_LEVEL = 1
MAX_LEVEL = 5


class Department(models.TextChoices):
    ENGINE = "engine", "Engine"
    AERODYNAMICS = "aerodynamics", "Aerodynamics"
    CHASSIS = "chassis", "Chassis"
    SUSPENSION = "suspension", "Suspension"
    ELECTRONICS = "electronics", "Electronics"


#: Maps a sponsor Affinity category to the department that receives a +1/-1
#: starting-level bonus at season start.
#: Direct department names (engine, aerodynamics, chassis, suspension, electronics)
#: are handled as fallback in get_starting_department_bonus() and don't need listing here.
AFFINITY_DEPARTMENT: dict[str, str] = {
    "speed": "engine",  # raw pace → engine power
    "development": "chassis",  # R&D investment → structural rigidity
    "consistency": "suspension",  # tyre management → compliant suspension
    "podiums": "aerodynamics",  # front-running → corner speed
    "wins": "engine",  # win focus → engine dominance (stacks with speed, clamped)
    # "points" and "money" have no department-level effect
}

#: Performance categories that modify sponsor payout rate per race.
#: Each entry maps a SponsorCondition category to:
#:   "condition"  – what the team must achieve this race ("win", "podium", "any_points", "fastest_lap")
#:   "bonus"      – fractional payout multiplier boost/penalty (e.g. 0.20 = ±20%)
#: Affinity (+1) applies the bonus as a reward; Penalty (-1) applies it as a deduction.
PAYOUT_CONDITION_BOOST: dict[str, dict] = {
    "wins": {"condition": "win", "bonus": 0.30},  # +30% if team wins
    "podiums": {"condition": "podium", "bonus": 0.20},  # +20% if team top-3
    "consistency": {"condition": "any_points", "bonus": 0.15},  # +15% if team scored
    "speed": {"condition": "fastest_lap", "bonus": 0.15},  # +15% if fastest lap
    "points": {"condition": "any_points", "bonus": 0.10},  # +10% if team scored
}

# Cost table for upgrades: cost to purchase an upgrade from level N -> N+1.
# Values are in the same credits unit used by Team.credits.
# Tune these to balance a 7-race season economy.
UPGRADE_COST_BY_LEVEL: dict[int, int] = {
    # Increased to balance season economy (see notes): costs double per level.
    1: 2000,  # cost to go 1->2
    2: 4000,  # 2->3
    3: 8000,  # 3->4
    4: 16000,  # 4->5
}
