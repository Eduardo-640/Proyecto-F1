from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("races", "0006_alter_credittransaction_transaction_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="RaceSessionSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_type", models.CharField(choices=[("practice", "Practice"), ("qualifying", "Qualifying"), ("race", "Race"), ("finished", "Finished")], default="race", max_length=20)),
                ("payload", models.JSONField(default=dict)),
                ("source_file", models.CharField(blank=True, max_length=255)),
                ("processed_at", models.DateTimeField(auto_now=True)),
                ("race", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="session_snapshots", to="races.race")),
            ],
            options={
                "verbose_name": "Race Session Snapshot",
                "verbose_name_plural": "Race Session Snapshots",
                "ordering": ["race", "session_type"],
                "unique_together": {("race", "session_type")},
            },
        ),
    ]
