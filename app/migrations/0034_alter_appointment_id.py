# Generated by Django 4.2.9 on 2024-01-11 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0033_alter_salesdata_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
