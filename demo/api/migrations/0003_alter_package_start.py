# Generated by Django 4.2.23 on 2025-07-07 18:25

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0002_add_permission_groups"),
    ]

    operations = [
        migrations.AlterField(
            model_name="package",
            name="start",
            field=models.DateField(default=api.models.now),
        ),
    ]
