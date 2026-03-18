from django.db import models
from apps.seasons.models import Season
from apps.teams.models import Team
from apps.races.constants import RaceStatus, TransactionType


class Race(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name="races")
    round_number = models.PositiveSmallIntegerField()
    circuit = models.ForeignKey(
        "Circuit", on_delete=models.CASCADE, related_name="races"
    )
    race_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RaceStatus.choices,
        default=RaceStatus.PRACTICE,
    )

    class Meta:
        ordering = ["season", "round_number"]
        unique_together = ["season", "round_number"]
        verbose_name = "Race"
        verbose_name_plural = "Races"

    def __str__(self):
        return f"Round {self.round_number} – {self.circuit} ({self.season})"


class RaceResult(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="results")
    driver = models.ForeignKey(
        "drivers.Driver", on_delete=models.CASCADE, related_name="race_results"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="race_results"
    )
    position = models.PositiveSmallIntegerField()
    pole_position = models.BooleanField(default=False)
    fastest_lap = models.BooleanField(default=False)
    finished_race = models.BooleanField(default=True)
    points_awarded = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ["race", "driver"]
        ordering = ["race", "position"]
        verbose_name = "Race Result"
        verbose_name_plural = "Race Results"

    def __str__(self):
        return f"{self.driver.name} – P{self.position} ({self.race})"


class CreditTransaction(models.Model):

    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.IntegerField()  # can be negative (expenses)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    description = models.CharField(max_length=255, blank=True)
    race = models.ForeignKey(
        Race,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Credit Transaction"
        verbose_name_plural = "Credit Transactions"

    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return (
            f"{self.team} {sign}{self.amount} ({self.get_transaction_type_display()})"
        )


class Circuit(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100, blank=True)
    laps = models.PositiveSmallIntegerField()
    length_km = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Length of the circuit in kilometers"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Circuit"
        verbose_name_plural = "Circuits"

    def __str__(self):
        return self.name
