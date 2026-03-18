from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.teams.models import Team
from apps.seasons.models import Season
from .constants import MIN_LEVEL, MAX_LEVEL, Department

level_field = lambda: models.PositiveSmallIntegerField(  # noqa: E731
    default=1,
    validators=[MinValueValidator(MIN_LEVEL), MaxValueValidator(MAX_LEVEL)],
)


class TeamDevelopment(models.Model):
    """Current technical development state of a team in a season."""

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="developments"
    )
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="developments"
    )

    engine = level_field()
    aerodynamics = level_field()
    chassis = level_field()
    suspension = level_field()
    electronics = level_field()

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["team", "season"]
        verbose_name = "Team Development"
        verbose_name_plural = "Team Developments"

    def __str__(self):
        return f"{self.team} – {self.season}"

    def get_level(self, department: str) -> int:
        return getattr(self, department)


class PurchasedUpgrade(models.Model):
    """History of upgrades purchased by a team."""

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="upgrades")
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name="upgrades"
    )
    department = models.CharField(max_length=20, choices=Department.choices)
    previous_level = models.PositiveSmallIntegerField()
    new_level = models.PositiveSmallIntegerField()
    cost = models.PositiveIntegerField()
    applied = models.BooleanField(default=False)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-purchased_at"]
        verbose_name = "Purchased Upgrade"
        verbose_name_plural = "Purchased Upgrades"

    def __str__(self):
        return f"{self.team} – {self.get_department_display()} {self.previous_level}→{self.new_level}"
