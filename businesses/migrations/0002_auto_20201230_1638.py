# Generated by Django 3.1.4 on 2020-12-30 16:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0002_orderoption"),
        ("businesses", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
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
                ("doctor_name", models.CharField(max_length=255)),
                ("patient_name", models.CharField(max_length=255)),
                ("patient_age", models.PositiveIntegerField()),
                ("referrer", models.CharField(max_length=255)),
                ("delivery_date", models.DateTimeField()),
                ("notes", models.TextField(blank=True, null=True)),
                ("is_urgent", models.BooleanField(default=False)),
                ("teeth", models.JSONField()),
                (
                    "latest_status",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("completed", "completed"),
                            ("delivered", "delivered"),
                            ("rework", "rework"),
                        ],
                        default="pending",
                        max_length=255,
                    ),
                ),
                (
                    "from_business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders_created",
                        to="businesses.business",
                    ),
                ),
                (
                    "from_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "options",
                    models.ManyToManyField(
                        related_name="orders", to="core.OrderOption"
                    ),
                ),
                (
                    "to_business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders_received",
                        to="businesses.business",
                    ),
                ),
                (
                    "to_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders_received",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Order",
                "verbose_name_plural": "Orders",
            },
        ),
        migrations.AlterField(
            model_name="businessaddress",
            name="address_type",
            field=models.CharField(
                choices=[("headquarters", "headquarters"), ("branch", "branch")],
                default="headquarters",
                max_length=12,
            ),
        ),
        migrations.CreateModel(
            name="OrderStatus",
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
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("completed", "completed"),
                            ("delivered", "delivered"),
                            ("rework", "rework"),
                        ],
                        default="pending",
                        max_length=255,
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_statuses",
                        to="businesses.order",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_statuses",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Order Status",
                "verbose_name_plural": "Order Statuses",
            },
        ),
    ]
