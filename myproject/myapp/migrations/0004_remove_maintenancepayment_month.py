# Generated by Django 5.0.6 on 2025-01-21 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_maintenancepayment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maintenancepayment',
            name='month',
        ),
    ]
