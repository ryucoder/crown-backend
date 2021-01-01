from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from core.models import PrimaryUUIDTimeStampedModel

from users.constants import USER_TYPE_CHOICES
from users.managers import UserManager


class EmailUser(PrimaryUUIDTimeStampedModel, AbstractUser):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    username = None
    email = models.EmailField("Email ID", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    user_type = models.CharField(
        max_length=12, choices=USER_TYPE_CHOICES, default="admin"
    )

    is_email_verified = models.BooleanField(default=False)
    mobile = models.BigIntegerField(default=0)
    is_mobile_verified = models.BooleanField(default=False)
    mobile_verified_time = models.DateTimeField(default=timezone.now)

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "Email User"
        verbose_name_plural = "Email Users"


class PasswordToken(PrimaryUUIDTimeStampedModel):
    email_user = models.ForeignKey(
        "users.EmailUser",
        related_name="reset_password_tokens",
        on_delete=models.CASCADE,
    )
    token = models.UUIDField()
    expiry = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = "Password Token"
        verbose_name_plural = "Password Tokens"
        unique_together = ["email_user", "token"]


class MobileToken(PrimaryUUIDTimeStampedModel):
    mobile = models.BigIntegerField()
    token = models.IntegerField()
    expiry = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"MobileToken - {self.id}"

    class Meta:
        verbose_name = "Mobile Token"
        verbose_name_plural = "Mobile Tokens"
