# Generated by Django 5.0.6 on 2025-01-23 12:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_remove_maintenancepayment_fid_complaint'),
    ]

    operations = [
        migrations.AddField(
            model_name='maintenancepayment',
            name='fid',
            field=models.ForeignKey(db_column='fid', null=True, on_delete=django.db.models.deletion.CASCADE, to='myapp.flat'),
        ),
    ]
