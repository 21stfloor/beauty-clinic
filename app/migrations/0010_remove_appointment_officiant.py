# Generated by Django 4.0.4 on 2023-08-26 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_appointment_status_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='officiant',
        ),
    ]
