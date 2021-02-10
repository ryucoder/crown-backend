from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from core.models import PrimaryUUIDTimeStampedModel

from users.constants import USER_TYPE_CHOICES, PASSWORD_CATEGORY_CHOICES
from users.managers import UserManager


class EmailUser(PrimaryUUIDTimeStampedModel, AbstractUser):

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    user_type = models.CharField(
        max_length=8, choices=USER_TYPE_CHOICES, default="employee"
    )

    email = models.EmailField("Email ID", unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_verified_time = models.DateTimeField(null=True, blank=True)

    mobile = models.BigIntegerField(default=0)
    is_mobile_verified = models.BooleanField(default=False)
    mobile_verified_time = models.DateTimeField(null=True, blank=True)

    @property
    def tokens(self):
        refresh = RefreshToken.for_user(self)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    @property
    def owners_business(self):
        business = "None"

        if self.employer:
            return self.employer.business

        return business

    def get_business(self):
        business = None 

        if self.user_type == "owner": 
            business = self.business
        else: 
            business = self.employer.business

        return business

    def __str__(self):
        return f"{self.email}"

    class Meta:
        verbose_name = "Email User"
        verbose_name_plural = "Email Users"


class PasswordToken(PrimaryUUIDTimeStampedModel):

    email_user = models.ForeignKey(
        "users.EmailUser",
        related_name="password_tokens",
        on_delete=models.CASCADE,
    )
    token = models.UUIDField()
    expiry = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    category = models.CharField(
        max_length=6, choices=PASSWORD_CATEGORY_CHOICES, default="signup"
    )

    used_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = "Password Token"
        verbose_name_plural = "Password Tokens"
        unique_together = ["email_user", "token"]


class MobileToken(PrimaryUUIDTimeStampedModel):
    email_user = models.ForeignKey(
        "users.EmailUser",
        related_name="mobile_tokens",
        on_delete=models.CASCADE,
    )
    mobile = models.BigIntegerField()
    token = models.IntegerField()
    expiry = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"MobileToken - {self.id}"

    class Meta:
        verbose_name = "Mobile Token"
        verbose_name_plural = "Mobile Tokens"
