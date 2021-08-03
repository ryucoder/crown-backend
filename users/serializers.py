import uuid

from businesses.models import (
    Business,
    BusinessConnect,
    BusinessEmployee,
)
from businesses.serializers import BusinessOnlySerializer
from core.serializers import ServerErrorSerializer
from core.utils import EmailUtil, TimeUtil
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.utils import TokenUtil
from users.constants import (
    CUSTOM_ERROR_MESSAGES,
    DEFAULT_USER_PASSWORD,
    MOBILE_TOKEN_EXPIRY_MINUTES,
    SIGNUP_TOKEN_EXPIRY_MINUTES,
)
from users.models import EmailUser, MobileToken, EmailToken


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=9, max_length=18)

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
        max_length=18,
        write_only=True,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )
    password_two = serializers.CharField(
        min_length=9,
        max_length=18,
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

    def validate_email(self, email):
        email = email.strip().lower()
        queryset = EmailUser.objects.filter(email__iexact=email)

        if queryset.exists():
            message = "server_exists_already"
            raise serializers.ValidationError(message)

        return email

    def validate_password_two(self, password_two):
        password_one = self.initial_data.get("password_one")

        if password_one != password_two:
            message = "server_passwords_not_match"
            raise serializers.ValidationError(message)

        return password_two

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
        verification_token = EmailToken()
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

        queryset = EmailToken.objects.filter(token=token, category="signup").order_by(
            "-created_at"
        )

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

        queryset = EmailToken.objects.filter(
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

        user_tokens = EmailToken.objects.order_by("-created_at").filter(
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
                message = "server_latest_token_unused"
                raise serializers.ValidationError(message)

        return data


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages=CUSTOM_ERROR_MESSAGES["EmailField"],
    )
    token = serializers.UUIDField(
        error_messages=CUSTOM_ERROR_MESSAGES["UUIDField"],
    )
    password_one = serializers.CharField(
        min_length=9,
        max_length=255,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )
    password_two = serializers.CharField(
        min_length=9,
        max_length=255,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )

    def validate_email(self, email):
        email = email.strip().lower()
        # token = self.initial_data["token"].strip()

        # TODO: same sql is being run twice, need a fix for this.
        queryset = EmailToken.objects.filter(email_user__email=email).order_by(
            "-created_at"
        )

        if not queryset.exists():
            message = "server_absent"
            raise serializers.ValidationError(message)

        return queryset.first()

    def validate_token(self, token):

        email = self.initial_data["email"].strip().lower()

        # TODO: same sql is being run twice, need a fix for this.
        queryset = EmailToken.objects.filter(
            email_user__email=email, token=token
        ).order_by("-created_at")

        if not queryset.exists():
            message = "server_absent"
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
        password_one = data["password_one"]
        password_two = data["password_two"]

        if password_one != password_two:
            message = "server_passwords_not_match"
            raise serializers.ValidationError(message)

        return data


class MobileTokenSerializer(serializers.ModelSerializer):
    def validate_mobile(self, mobile):
        len_mobile = len(str(mobile).strip())

        if len_mobile < 10:
            message = "server_min_length"
            raise serializers.ValidationError(message)

        if len_mobile > 10:
            message = "server_max_length"
            raise serializers.ValidationError(message)

        queryset = EmailUser.objects.filter(mobile=mobile)

        if not queryset.exists():
            message = "server_mobile_absent"
            raise serializers.ValidationError(message)

        latest_token = (
            MobileToken.objects.filter(mobile=mobile).order_by("-created_at").first()
        )

        if latest_token != None:
            if timezone.now() < latest_token.expiry:
                message = "server_mobile_token_not_expired"
                raise serializers.ValidationError(message)

        return queryset.first()

    def create(self, validated_data):

        email_user = validated_data.pop("mobile")

        instance = MobileToken()
        instance.email_user = email_user
        instance.mobile = email_user.mobile
        instance.token = TokenUtil.get_mobile_token()
        instance.expiry = TimeUtil.get_minutes_from_now(MOBILE_TOKEN_EXPIRY_MINUTES)
        instance.is_used = False

        instance.save()

        # NOTE: SHOULD HAPPEN SYNCHRNOUSLY ONLY. CELERY TASK SHOULD NOT BE CREATED FOR THIS.
        # SmsUtil.send_mobile_token_sms(instance)

        return instance

    class Meta:
        model = MobileToken
        fields = ["mobile", "token", "expiry"]
        read_only_fields = ["token", "expiry"]


class VerifyMobileTokenSerializer(serializers.ModelSerializer):
    def validate_token(self, token):

        mobile = self.initial_data["mobile"]

        latest_token = (
            MobileToken.objects.filter(mobile=mobile, token=token)
            .order_by("-created_at")
            .first()
        )

        if latest_token == None:
            message = "server__absent"
            raise serializers.ValidationError(message)

        else:
            if timezone.now() > latest_token.expiry:
                message = "server_expired"
                raise serializers.ValidationError(message)

            if latest_token.is_used:
                message = "server_used_already"
                raise serializers.ValidationError(message)

        return latest_token

    def validate_mobile(self, mobile):
        len_mobile = len(str(mobile).strip())

        if len_mobile < 10:
            message = "server_min_length"
            raise serializers.ValidationError(message)

        if len_mobile > 10:
            message = "server_max_length"
            raise serializers.ValidationError(message)

        queryset = EmailUser.objects.filter(mobile=mobile)

        if not queryset.exists():
            message = "server_mobile_absent"
            raise serializers.ValidationError(message)

        return queryset.first()

    def create(self, validated_data):

        token = validated_data.pop("token")

        token.is_used = True
        token.used_time = TimeUtil.get_minutes_from_now(0)

        token.save()

        # NOTE: SHOULD HAPPEN SYNCHRNOUSLY ONLY. CELERY TASK SHOULD NOT BE CREATED FOR THIS.
        # SmsUtil.send_mobile_token_sms(instance)

        return token

    class Meta:
        model = MobileToken
        fields = ["mobile", "token", "expiry"]
        read_only_fields = ["expiry"]


class CreateRelatedBusinessSerializer(serializers.ModelSerializer):
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
            "company_name",
        ]

    def create(self, validated_data):
        company_name = validated_data.pop("company_name")

        instance = EmailUser(**validated_data)
        instance.password = make_password(DEFAULT_USER_PASSWORD)
        instance.user_type = "owner"
        instance.is_email_verified = False
        instance.is_mobile_verified = False

        # # EMAIL TOKEN
        # verification_token = EmailToken()
        # verification_token.email_user = instance
        # verification_token.token = uuid.uuid4()
        # verification_token.category = "signup"
        # verification_token.is_used = False
        # verification_token.expiry = TimeUtil.get_minutes_from_now(
        #     SIGNUP_TOKEN_EXPIRY_MINUTES
        # )

        user_id = self.context["user_id"]

        users_business = (
            EmailUser.objects.filter(id=user_id)
            .select_related("business")
            .first()
            .get_business()
        )

        # Business
        business = Business()
        business.name = company_name
        business.owner = instance
        business.category = (
            "dentist" if users_business.category == "laboratory" else "laboratory"
        )
        business.is_active = True

        connect = BusinessConnect()
        related_business = business

        if users_business.category == "dentist":
            connect.dentist = users_business
            connect.laboratory = related_business

        else:
            connect.dentist = related_business
            connect.laboratory = users_business

        with transaction.atomic():
            instance.save()
            # verification_token.save()
            business.save()
            connect.save()

        return instance


class ConnectRelatedBusinessSerializer(serializers.ModelSerializer):
    business_id = serializers.UUIDField(
        write_only=True,
        error_messages=CUSTOM_ERROR_MESSAGES["UUIDField"],
    )

    def validate_business_id(self, business_id):
        user = self.context["user"]

        user_business = user.get_business()
        business = Business.objects.filter(id=business_id).first()

        if business is None:
            message = "server_absent"
            raise serializers.ValidationError(message)

        if user_business.category == business.category:
            message = "server_invalid"
            raise serializers.ValidationError(message)

        if user_business.category == "dentist":
            dentist_id = user_business.id
            laboratory_id = business.id
        else:
            dentist_id = business.id
            laboratory_id = user_business.id

        queryset = BusinessConnect.objects.filter(
            dentist_id=dentist_id, laboratory_id=laboratory_id
        )
        if queryset.exists():
            message = "server_exists_already"
            raise serializers.ValidationError(message)

        return business

    class Meta:
        model = BusinessConnect
        fields = [
            "id",
            "dentist",
            "laboratory",
            "is_active",
            "business_id",
        ]
        read_only_fields = ["dentist", "laboratory", "is_active"]

    def create(self, validated_data):

        user = self.context["user"]

        connect = BusinessConnect()
        users_business = user.get_business()
        related_business = validated_data["business_id"]

        if users_business.category == "dentist":
            connect.dentist = users_business
            connect.laboratory = related_business

        else:
            connect.dentist = related_business
            connect.laboratory = users_business

        with transaction.atomic():
            connect.save()

        return connect


class ToggleBusinessConnectSerializer(serializers.ModelSerializer):
    connect_id = serializers.UUIDField(
        write_only=True,
        error_messages=CUSTOM_ERROR_MESSAGES["UUIDField"],
    )

    def validate_connect_id(self, connect_id):

        queryset = BusinessConnect.objects.filter(id=connect_id)
        if not queryset.exists():
            message = "server_absent"
            raise serializers.ValidationError(message)

        return queryset.first()

    class Meta:
        model = BusinessConnect
        fields = [
            "id",
            "dentist",
            "laboratory",
            "is_active",
            "connect_id",
        ]
        read_only_fields = ["dentist", "laboratory", "is_active"]

    def create(self, validated_data):

        connect = validated_data["connect_id"]
        connect.is_active = False if connect.is_active else True
        connect.save()

        return connect


class BusinessEmployeeSerializer(serializers.ModelSerializer):
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
        max_length=18,
        write_only=True,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )
    password_two = serializers.CharField(
        min_length=9,
        max_length=18,
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
    mobile = serializers.CharField(
        min_length=10,
        max_length=10,
        required=False,
        error_messages=CUSTOM_ERROR_MESSAGES["CharField"],
    )

    def validate_email(self, email):
        email = email.strip().lower()
        queryset = EmailUser.objects.filter(email__iexact=email)

        if queryset.exists():
            message = "server_exists_already"
            raise serializers.ValidationError(message)

        return email

    def validate_password_two(self, password_two):
        password_one = self.initial_data.get("password_one")

        if password_one != password_two:
            message = "server_passwords_not_match"
            raise serializers.ValidationError(message)

        return password_two

    def validate_mobile(self, mobile):

        if not mobile.isnumeric():
            message = "server_must_be_numeric"
            raise serializers.ValidationError(message)

        return mobile

    class Meta:
        model = EmailUser
        fields = [
            "password_one",
            "password_two",
            "id",
            "first_name",
            "last_name",
            "email",
            "is_email_verified",
            "mobile",
            "is_mobile_verified",
        ]
        read_only_fields = ["is_email_verified", "is_mobile_verified"]

    def create(self, validated_data):
        user = self.context["user"]
        password_one = validated_data.pop("password_one")
        password_two = validated_data.pop("password_two")

        employee = EmailUser(**validated_data)
        employee.password = make_password(password_one)
        employee.user_type = "employee"
        employee.is_email_verified = False
        employee.is_mobile_verified = False

        # Business
        employment = BusinessEmployee()
        employment.business = user.get_business()
        employment.employee = employee

        # EMAIL TOKEN
        email_token = EmailToken()
        email_token.email_user = employee
        email_token.token = uuid.uuid4()
        email_token.category = "signup"
        email_token.is_used = False
        email_token.expiry = TimeUtil.get_minutes_from_now(SIGNUP_TOKEN_EXPIRY_MINUTES)

        # Mobile TOKEN
        mobile = validated_data.get("mobile", None)
        if mobile:
            mobile_token = MobileToken()
            mobile_token.email_user = employee
            mobile_token.mobile = employee.mobile
            mobile_token.token = TokenUtil.get_mobile_token()
            mobile_token.expiry = TimeUtil.get_minutes_from_now(
                MOBILE_TOKEN_EXPIRY_MINUTES
            )
            mobile_token.is_used = False

        with transaction.atomic():
            employee.save()
            employment.save()
            email_token.save()

            if mobile:
                mobile_token.save()

        # EmailUtil.send_signup_email(instance, email_token)

        return employee
