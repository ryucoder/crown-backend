# Generated by Django 2.2.2 on 2020-12-30 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ResetPasswordToken",
            new_name="PasswordToken",
        ),
        migrations.AlterModelOptions(
            name="passwordtoken",
            options={
                "verbose_name": "Password Token",
                "verbose_name_plural": "Password Tokens",
            },
        ),
    ]
