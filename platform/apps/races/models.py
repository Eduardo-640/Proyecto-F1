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
        # allow multiple session records (practice/qualifying/race) per round
        unique_together = [["season", "round_number", "status"]]
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
    laps_completed = models.PositiveSmallIntegerField(default=0)
    total_time = models.BigIntegerField(null=True, blank=True)
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
    assetto_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Name used by Assetto Corsa/assetto servers",
    )
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


class RaceSessionSnapshot(models.Model):
    """Stores the raw Assetto Corsa JSON payload for a processed session."""

    race = models.ForeignKey(
        Race, on_delete=models.CASCADE, related_name="session_snapshots"
    )
    session_type = models.CharField(
        max_length=20, choices=RaceStatus.choices, default=RaceStatus.RACE
    )
    payload = models.JSONField(default=dict)
    source_file = models.CharField(max_length=255, blank=True)
    processed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["race", "session_type"]
        ordering = ["race", "session_type"]
        verbose_name = "Race Session Snapshot"
        verbose_name_plural = "Race Session Snapshots"

    def __str__(self):
        return f"{self.race} – {self.get_session_type_display()} snapshot"
