import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("developments", "0001_initial"),
        ("seasons", "0001_initial"),
        ("teams", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CarSetupSnapshot",
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
                ("version", models.PositiveSmallIntegerField()),
                ("ini_content", models.TextField()),
                ("params_json", models.JSONField(default=dict)),
                ("changed_params", models.JSONField(blank=True, default=dict)),
                ("preset_bias", models.CharField(blank=True, max_length=30)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "season",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="setup_snapshots",
                        to="seasons.season",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="setup_snapshots",
                        to="teams.team",
                    ),
                ),
                (
                    "upgrade",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="setup_snapshot",
                        to="developments.purchasedupgrade",
                    ),
                ),
            ],
            options={
                "verbose_name": "Car Setup Snapshot",
                "verbose_name_plural": "Car Setup Snapshots",
                "ordering": ["team", "season", "version"],
                "unique_together": {("team", "season", "version")},
            },
        ),
    ]
