from django.db import models


class Affinity(models.TextChoices):
    PODIUMS = "podiums", "Podiums"
    WINS = "wins", "Wins"
    DEVELOPMENT = "development", "Development"
    MONEY = "money", "Money"
    POINTS = "points", "Points"
    SPEED = "speed", "Speed"
    CONSISTENCY = "consistency", "Consistency"


class SponsorConditionType(models.TextChoices):
    AFFINITY = "affinity", "Affinity"  # rewards
    PENALTY = "penalty", "Penalty"  # dislikes / penalizes'
    NEUTRAL = "neutral", "Neutral"  # no effect / neutral
