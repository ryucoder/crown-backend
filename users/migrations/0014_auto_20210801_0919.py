# Generated by Django 3.1.4 on 2021-08-01 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20210222_1002'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PasswordToken',
            new_name='EmailToken',
        ),
    ]