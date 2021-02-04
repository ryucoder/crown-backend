import uuid

from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from core.serializers import ServerErrorSerializer
from core.utils import EmailUtil, TimeUtil

from users.models import EmailUser, PasswordToken
from users.constants import SIGNUP_TOKEN_EXPIRY_MINUTES, CUSTOM_ERROR_MESSAGES

from businesses.models import Business
from businesses.serializers import BusinessOnlySerializer


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)

    def validate(self, data):
        email_absent = False
        password_matched = False

        email = data["email"].strip().lower()
        password = data["password"].strip()

        try:
            user = EmailUser.objects.get(email=email)
        except EmailUser.DoesNotExist:
            email_absent = True

        if (not email_absent) and user.check_password(password):
            password_matched = True

        if (email_absent == True) or (password_matched == False):
            message = "invalid_email_or_passsword"
            raise serializers.ValidationError(message)

        data["user"] = user
        return data


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "user_type",
            "is_email_verified",
            "is_mobile_verified",
            "tokens",
        ]


class EmailUserWithBusinessSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super(EmailUserWithBusinessSerializer, self).__init__(*args, **kwargs)

        if self.instance is not None:
            if self.instance.user_type == "owner":
                self.fields["business"] = BusinessOnlySerializer()

            if self.instance.user_type == "employee":
                self.fields["owners_business"] = BusinessOnlySerializer(
                    instance=self.instance.employer.business
                )

    class Meta:
        model = EmailUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "user_type",
            "is_email_verified",
            "is_mobile_verified",
            "tokens",
            "business",
        ]


class LaboratorySignUpSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        max_length=255,
        required=True,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )
    last_name = serializers.CharField(
        max_length=255,
        required=True,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )
    password_one = serializers.CharField(
        min_length=9,
        max_length=255,
        write_only=True,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )
    password_two = serializers.CharField(
        min_length=9,
        max_length=255,
        write_only=True,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )

    company_name = serializers.CharField(
        max_length=255,
        write_only=True,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )

    email = serializers.EmailField(
        max_length=255,
        error_messages=CUSTOM_ERROR_MESSAGES["EmailField"],
        validators=[
            UniqueValidator(
                queryset=EmailUser.objects.all(), message="server_exists_already"
            )
        ],
    )

    def validate(self, data):
        password_one = data["password_one"]
        password_two = data["password_two"]

        if password_one != password_two:
            message = "passwords_not_match"
            raise serializers.ValidationError(message)

        return data

    def validate_email(self, email):
        email = email.strip().lower()
        queryset = EmailUser.objects.filter(email__iexact=email)

        if queryset.exists():
            message = "server_exists_already"
            raise serializers.ValidationError(message)

        return email

    class Meta:
        model = EmailUser
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "password_one",
            "password_two",
            "company_name",
        ]

    def create(self, validated_data):
        password_one = validated_data.pop("password_one")
        password_two = validated_data.pop("password_two")
        company_name = validated_data.pop("company_name")

        instance = EmailUser(**validated_data)
        instance.password = make_password(password_one)
        instance.user_type = "owner"
        instance.is_email_verified = False

        # EMAIL TOKEN
        verification_token = PasswordToken()
        verification_token.email_user = instance
        verification_token.token = uuid.uuid4()
        verification_token.category = "signup"
        verification_token.is_used = False
        verification_token.expiry = TimeUtil.get_minutes_from_now(
            SIGNUP_TOKEN_EXPIRY_MINUTES
        )

        # Business
        business = Business()
        business.name = company_name
        business.owner = instance
        business.category = "laboratory"
        business.is_active = True

        with transaction.atomic():
            instance.save()
            verification_token.save()
            business.save()

        EmailUtil.send_signup_email(instance, verification_token)

        return instance


class LaboratoryVerifySignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages=CUSTOM_ERROR_MESSAGES["EmailField"],
    )
    token = serializers.UUIDField(
        error_messages=CUSTOM_ERROR_MESSAGES["UUIDField"],
    )

    def validate_email(self, email):
        email = email.strip().lower()

        queryset = EmailUser.objects.filter(email=email)

        if not queryset.exists():
            message = "server_absent"
            raise serializers.ValidationError(message)

        return queryset.first()

    def validate_token(self, token):

        email = self.initial_data["email"].strip().lower()

        queryset = PasswordToken.objects.filter(
            token=token, category="signup"
        ).order_by("-created_at")

        if not queryset.exists():
            # NOTE: message should be server_absent, but for this endpoint server_invalid is chosen
            message = "server_invalid"
            raise serializers.ValidationError(message)

        token_object = queryset.first()

        if token_object.is_used:
            message = "server_used"
            raise serializers.ValidationError(message)

        if token_object.expiry < timezone.now():
            message = "server_expired"
            raise serializers.ValidationError(message)

        return token_object

    def validate(self, data):
        email_user = data["email"]
        token_object = data["token"]

        queryset = PasswordToken.objects.filter(
            email_user_id=email_user.id, token=token_object.token, category="signup"
        ).order_by("-created_at")

        if not queryset.exists():
            message = "server_email_token_mismatch"
            raise serializers.ValidationError(message)

        return data

    class Meta:
        fields = ["email", "token"]


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages=CUSTOM_ERROR_MESSAGES["EmailField"],
    )

    def validate_email(self, email):
        email = email.strip().lower()

        queryset = EmailUser.objects.filter(email=email)

        if not queryset.exists():
            message = "server_absent"
            raise serializers.ValidationError(message)

        return queryset.first()

    def validate(self, data):

        is_initial = False

        email_user = data["email"]

        user_tokens = PasswordToken.objects.order_by("-created_at").filter(
            email_user=email_user, category="reset"
        )

        if user_tokens.exists():
            latest_token = user_tokens.first()

        else:
            is_initial = True

        if is_initial == False:
            if (latest_token.is_used == False) and (
                latest_token.expiry > timezone.now()
            ):
                message = "latest_token_unused_and_not_expired"
                raise serializers.ValidationError(message)

        return data
