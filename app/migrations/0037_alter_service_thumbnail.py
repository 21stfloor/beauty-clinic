# Generated by Django 4.2.9 on 2024-01-11 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0036_alter_order_id_alter_salesdata_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service",
            name="thumbnail",
            field=models.ImageField(
                blank=True, default="app_icon.png", null=True, upload_to="services/"
            ),
        ),
    ]
