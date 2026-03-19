from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("races", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="circuit",
            name="assetto_name",
            field=models.CharField(
                max_length=150,
                null=True,
                blank=True,
                help_text="Name used by Assetto Corsa/assetto servers",
            ),
        ),
    ]
