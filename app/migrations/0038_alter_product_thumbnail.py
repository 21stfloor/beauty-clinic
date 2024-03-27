# Generated by Django 4.2.9 on 2024-01-11 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0037_alter_service_thumbnail"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="thumbnail",
            field=models.ImageField(
                blank=True, default="app_icon.png", null=True, upload_to="services/"
            ),
        ),
    ]
