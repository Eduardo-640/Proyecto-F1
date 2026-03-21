from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teams", "0003_sponsor_total_score_alter_sponsorcondition_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sponsorcondition",
            name="type",
            field=models.CharField(
                choices=[
                    ("affinity", "Affinity"),
                    ("penalty", "Penalty"),
                    ("neutral", "Neutral"),
                ],
                max_length=20,
                blank=True,
                null=True,
            ),
        ),
    ]
