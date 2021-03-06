# Generated by Django 3.1.4 on 2021-02-03 13:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0008_delete_mobiletoken"),
    ]

    operations = [
        migrations.CreateModel(
            name="MobileToken",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("mobile", models.BigIntegerField()),
                ("token", models.IntegerField()),
                ("expiry", models.DateTimeField()),
                ("is_used", models.BooleanField(default=False)),
                (
                    "email_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mobile_tokens",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Mobile Token",
                "verbose_name_plural": "Mobile Tokens",
            },
        ),
    ]
