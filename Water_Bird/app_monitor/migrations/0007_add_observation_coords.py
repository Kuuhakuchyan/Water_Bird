# Generated migration: only adds latitude/longitude to ObservationRecord
# Does NOT touch GIS fields to avoid SQLite compatibility issues
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_monitor", "0006_alter_product_options_observationrecord_description"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="observationrecord",
            name="latitude",
            field=models.FloatField(blank=True, null=True, verbose_name="纬度"),
        ),
        migrations.AddField(
            model_name="observationrecord",
            name="longitude",
            field=models.FloatField(blank=True, null=True, verbose_name="经度"),
        ),
        migrations.AlterField(
            model_name="observationrecord",
            name="zone",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="app_monitor.wetlandzone",
                verbose_name="监测点位",
            ),
        ),
    ]
