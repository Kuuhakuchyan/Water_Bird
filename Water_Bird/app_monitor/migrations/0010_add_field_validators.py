# Auto-generated migration for field validators
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ("app_monitor", "0009_add_species_image_gallery"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aidetectionresult",
            name="confidence",
            field=models.FloatField(
                default=0.0,
                validators=[
                    django.core.validators.MinValueValidator(0.0),
                    django.core.validators.MaxValueValidator(1.0),
                ],
                verbose_name="置信度",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="stock",
            field=models.IntegerField(
                default=999,
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="库存",
            ),
        ),
    ]
