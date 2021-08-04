# Generated by Django 3.1.4 on 2021-08-04 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0018_auto_20210804_0546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='delivery_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='latest_status',
            field=models.CharField(choices=[('onhold', 'onhold'), ('pending', 'pending'), ('working', 'working'), ('completed', 'completed'), ('delivered', 'delivered'), ('rework', 'rework')], default='pending', max_length=255),
        ),
        migrations.AlterField(
            model_name='orderstatus',
            name='status',
            field=models.CharField(choices=[('onhold', 'onhold'), ('pending', 'pending'), ('working', 'working'), ('completed', 'completed'), ('delivered', 'delivered'), ('rework', 'rework')], default='pending', max_length=255),
        ),
    ]