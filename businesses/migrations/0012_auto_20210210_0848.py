# Generated by Django 3.1.4 on 2021-02-10 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('businesses', '0011_businesscontact_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='referrer',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]