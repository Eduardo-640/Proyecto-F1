from django.db import models

MIN_LEVEL = 1
MAX_LEVEL = 5


class Department(models.TextChoices):
    ENGINE = "engine", "Engine"
    AERODYNAMICS = "aerodynamics", "Aerodynamics"
    CHASSIS = "chassis", "Chassis"
    SUSPENSION = "suspension", "Suspension"
    ELECTRONICS = "electronics", "Electronics"


#: Maps a sponsor Affinity category to the department that receives a +1
#: starting-level bonus when that affinity is the team's dominant one.
#: Categories not listed here grant no department bonus.
AFFINITY_DEPARTMENT: dict[str, str] = {
    "speed": "engine",  # raw pace focus → engine power
    "wins": "engine",  # win-focused → engine dominance
    "podiums": "aerodynamics",  # consistent front-running → corner speed
    "development": "chassis",  # R&D investment → structural rigidity
    "consistency": "suspension",  # tyre management → compliant suspension
    "money": "electronics",  # financial muscle → resource-intensive tech
    # "points" has no single department bias
}
