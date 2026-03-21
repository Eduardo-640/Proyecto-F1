from django.db import models


class RaceStatus(models.TextChoices):
    PRACTICE = "practice", "Practice"
    QUALIFYING = "qualifying", "Qualifying"
    RACE = "race", "Race"
    FINISHED = "finished", "Finished"


class TransactionType(models.TextChoices):
    RACE_RESULT = "race_result", "Race Result"
    BALANCE_BONUS = "balance_bonus", "Competitive Balance Bonus"
    UPGRADE_PURCHASE = "upgrade_purchase", "Upgrade Purchase"
    ADMIN_ADJUSTMENT = "admin_adjustment", "Administrative Adjustment"
    SPONSOR_BASE = "sponsor_base", "Sponsor Base Bonus"
    SPONSOR_PAYOUT = "sponsor_payout", "Sponsor Payout"
