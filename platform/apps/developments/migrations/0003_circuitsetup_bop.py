import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("developments", "0002_carsetupsnapshot"),
        ("races", "0001_initial"),
        ("seasons", "0001_initial"),
        ("teams", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BalanceOfPerformance",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ballast", models.IntegerField(default=0)),
                (
                    "restrictor_pct",
                    models.PositiveSmallIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(100)],
                    ),
                ),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bop_entries",
                        to="seasons.season",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bop_entries",
                        to="teams.team",
                    ),
                ),
            ],
            options={
                "verbose_name": "Balance of Performance",
                "verbose_name_plural": "Balance of Performance Entries",
                "unique_together": {("team", "season")},
            },
        ),
        migrations.CreateModel(
            name="CircuitSetup",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tunable_overrides", models.JSONField(blank=True, default=dict)),
                ("ini_content", models.TextField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "base_snapshot",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="circuit_setups",
                        to="developments.carsetupsnapshot",
                    ),
                ),
                (
                    "circuit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="circuit_setups",
                        to="races.circuit",
                    ),
                ),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="circuit_setups",
                        to="seasons.season",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="circuit_setups",
                        to="teams.team",
                    ),
                ),
            ],
            options={
                "verbose_name": "Circuit Setup",
                "verbose_name_plural": "Circuit Setups",
                "ordering": ["team", "season", "circuit"],
                "unique_together": {("team", "season", "circuit")},
            },
        ),
    ]
