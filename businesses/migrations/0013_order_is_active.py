# Generated by Django 3.1.4 on 2021-02-10 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0012_auto_20210210_0848'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]