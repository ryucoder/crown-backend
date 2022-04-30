# Generated by Django 3.1.4 on 2022-04-30 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("businesses", "0023_auto_20220409_1618"),
    ]

    operations = [
        migrations.AddField(
            model_name="business",
            name="referral",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="referrals",
                to="businesses.business",
            ),
        ),
    ]
