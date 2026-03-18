from django.db import models

MIN_LEVEL = 1
MAX_LEVEL = 5


class Department(models.TextChoices):
    ENGINE = "engine", "Engine"
    AERODYNAMICS = "aerodynamics", "Aerodynamics"
    CHASSIS = "chassis", "Chassis"
    SUSPENSION = "suspension", "Suspension"
    ELECTRONICS = "electronics", "Electronics"
