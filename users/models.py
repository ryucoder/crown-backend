from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from core.models import PrimaryUUIDTimeStampedModel

from users.constants import USER_TYPE_CHOICES
from users.managers import UserManager


class State(PrimaryUUIDTimeStampedModel):
    name = models.CharField(max_length=255)
    gst_code = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.gst_code}"

    class Meta:
        verbose_name = "State"
        verbose_name_plural = "States"


class EmailUserAddress(PrimaryUUIDTimeStampedModel):
    ADDRESS_CHOICES = [
        ("billing", "billing"),
        ("shipping", "shipping"),
    ]
    gstin = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    pincode = models.CharField(max_length=6)
    address_type = models.CharField(
        max_length=8, choices=ADDRESS_CHOICES, default="billing"
    )

    user = models.ForeignKey(
        "users.EmailUser", on_delete=models.CASCADE, related_name="addresses"
    )

    state = models.ForeignKey(
        "users.State", on_delete=models.PROTECT, related_name="addresses"
    )

    is_default = models.BooleanField(default=True)

    class Meta:
        verbose_name = "EmailUser Address"
        verbose_name_plural = "EmailUser Addresses"
        ordering = ["user", "address_type"]


class EmailUser(PrimaryUUIDTimeStampedModel, AbstractUser):

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


class BankAccount(PrimaryUUIDTimeStampedModel):

    BANK_ACCOUNT_TYPE_CHOICES = [
        ("current", "current"),
        ("savings", "savings"),
    ]
    account_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=11)
    account_type = models.CharField(
        max_length=255, default="current", choices=BANK_ACCOUNT_TYPE_CHOICES
    )

    email_user = models.ForeignKey(
        "users.EmailUser", related_name="bank_accounts", on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Bank Account"
        verbose_name_plural = "Bank Accounts"
