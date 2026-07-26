from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newapp", "0004_alter_touristattraction_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="accommodation",
            name="latitude",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="accommodation",
            name="longitude",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
