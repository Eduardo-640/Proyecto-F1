from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("races", "0003_allow_session_per_round"),
    ]

    operations = [
        migrations.AddField(
            model_name="raceresult",
            name="laps_completed",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="raceresult",
            name="total_time",
            field=models.BigIntegerField(blank=True, null=True),
        ),
    ]
