from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("races", "0002_assetto_name"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="race",
            unique_together={("season", "round_number", "status")},
        ),
    ]
