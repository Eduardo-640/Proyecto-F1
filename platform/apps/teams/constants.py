from django.db import models


class Affinity(models.TextChoices):
    # Car departments
    ENGINE = "engine", "Engine"
    AERODYNAMICS = "aerodynamics", "Aerodynamics"
    ELECTRONICS = "electronics", "Electronics"
    CHASSIS = "chassis", "Chassis"
    SUSPENSION = "suspension", "Suspension"
    # Performance metrics
    DEVELOPMENT = "development", "Development"
    CONSISTENCY = "consistency", "Consistency"
    PODIUMS = "podiums", "Podiums"
    WINS = "wins", "Wins"
    POINTS = "points", "Points"
    SPEED = "speed", "Speed"
    # Economy
    MONEY = "money", "Money"


class SponsorConditionType(models.TextChoices):
    AFFINITY = "affinity", "Affinity"  # rewards
    PENALTY = "penalty", "Penalty"  # dislikes / penalizes'
    NEUTRAL = "neutral", "Neutral"  # no effect / neutral
