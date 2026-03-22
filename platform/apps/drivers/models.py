from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from apps.teams.models import Team


class Driver(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    number = models.PositiveIntegerField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    team = models.OneToOneField(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driver",
    )
    steam_id = models.CharField(max_length=64, blank=True, null=True, unique=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        if raw_password:
            self.password = make_password(raw_password)
        else:
            self.password = None

    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password(raw_password, self.password)

    def has_usable_password(self):
        return bool(self.password)

    class Meta:
        ordering = ["name"]
        verbose_name = "Driver"
        verbose_name_plural = "Drivers"

    def __str__(self):
        return f"{self.name} {self.last_name}"


class DriverStanding(models.Model):
    """Accumulated standings for a driver within a season."""

    driver = models.ForeignKey(
        Driver,
        on_delete=models.CASCADE,
        related_name="standings",
    )
    season = models.ForeignKey(
        "seasons.Season",
        on_delete=models.CASCADE,
        related_name="driver_standings",
    )
    total_points = models.PositiveIntegerField(default=0)
    races_entered = models.PositiveSmallIntegerField(default=0)
    wins = models.PositiveSmallIntegerField(default=0)
    podiums = models.PositiveSmallIntegerField(default=0)
    pole_positions = models.PositiveSmallIntegerField(default=0)
    fastest_laps = models.PositiveSmallIntegerField(default=0)
    dnf_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ["driver", "season"]
        ordering = ["season", "-total_points"]
        verbose_name = "Driver Standing"
        verbose_name_plural = "Driver Standings"

    def __str__(self):
        return f"{self.driver.name} – {self.season} ({self.total_points} pts)"


class DriverPointTransaction(models.Model):
    """Audit record for point changes applied to a driver."""

    driver = models.ForeignKey(
        Driver, on_delete=models.CASCADE, related_name="point_transactions"
    )
    season = models.ForeignKey(
        "seasons.Season",
        on_delete=models.CASCADE,
        related_name="driver_point_transactions",
    )
    amount = models.IntegerField(help_text="Delta points (can be negative)")
    race = models.ForeignKey(
        "races.Race",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="driver_point_transactions",
    )
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Driver Point Transaction"
        verbose_name_plural = "Driver Point Transactions"

    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"{self.driver.name} {sign}{self.amount} pts ({self.season})"
