from django.db import models
from .constants import Affinity, SponsorConditionType


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    credits = models.PositiveIntegerField(default=500)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-credits"]
        verbose_name = "Team"
        verbose_name_plural = "Teams"

    def __str__(self):
        return self.name


class Sponsor(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sponsors",
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_main = models.BooleanField(default=False)
    base_bonus = models.PositiveIntegerField(
        default=0, help_text="Credits provided to the team per season"
    )
    active = models.BooleanField(default=True)
    total_score = models.IntegerField(
        default=0,
        help_text="Sum of all non-money condition values (affinities and penalties).",
    )

    class Meta:
        verbose_name = "Sponsor"
        verbose_name_plural = "Sponsors"
        constraints = [
            models.UniqueConstraint(
                fields=["team"],
                condition=models.Q(is_main=True),
                name="unique_main_sponsor_per_team",
            )
        ]

    def __str__(self):
        return self.name


class SponsorCondition(models.Model):
    """Represents an affinity or penalty of a sponsor."""

    sponsor = models.ForeignKey(
        Sponsor,
        on_delete=models.CASCADE,
        related_name="conditions",
    )
    type = models.CharField(
        max_length=20, choices=SponsorConditionType.choices, blank=True, null=True
    )
    category = models.CharField(max_length=20, choices=Affinity.choices)
    value = models.IntegerField(
        default=0,
        help_text="Bonus credits (positive) or penalty (negative)",
    )
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Sponsor Condition"
        verbose_name_plural = "Sponsor Conditions"

    def __str__(self):
        return f"{self.sponsor.name} | {self.get_type_display()} | {self.get_category_display()}"


class SponsorPayout(models.Model):
    """Represents scheduled / pending sponsor payments tied to a season.

    The management command `apply_sponsor_base` will create a payout record
    for any remainder after an upfront portion has been applied.
    """

    sponsor = models.ForeignKey(
        Sponsor, on_delete=models.CASCADE, related_name="payouts"
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="sponsor_payouts"
    )
    season = models.ForeignKey(
        "seasons.Season", on_delete=models.CASCADE, related_name="sponsor_payouts"
    )
    total_amount = models.PositiveIntegerField()
    remaining_amount = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sponsor Payout"
        verbose_name_plural = "Sponsor Payouts"

    def __str__(self):
        return f"{self.sponsor.name} → {self.team} ({self.remaining_amount}/{self.total_amount})"
