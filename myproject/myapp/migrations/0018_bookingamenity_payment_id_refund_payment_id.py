# Generated by Django 5.0.6 on 2025-02-10 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_alter_refund_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingamenity',
            name='payment_id',
            field=models.CharField(blank=True, default='xyz', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='refund',
            name='payment_id',
            field=models.CharField(blank=True, default='xyz', max_length=50, null=True),
        ),
    ]
