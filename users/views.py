from decimal import Context

from django.db.models import query
from core.utils import CommonUtil, EmailUtil, TimeUtil
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response

from users import serializers
from users.constants import RESET_PASSWORD_TOKEN_EXPIRY_MINUTES
from users.models import EmailUser, EmailToken
from users.utils import TokenUtil

# from rest_framework_simplejwt.authentication import (
#     JWTAuthentication,
#     JWTTokenUserAuthentication,
# )


# login
# signup - Dental Lab
# confirm email
# confirm mobile
# request reset password
# reset password


class EmailUserViewset(RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        return (
            EmailUser.objects.all()
            .select_related("owned_business")
            .prefetch_related("owned_business__business")
        )

    def get_serializer_class(self):

        if self.action == "login":
            return serializers.LoginSerializer

        if self.action == "laboratory_signup":
            return serializers.LaboratorySignUpSerializer

        if self.action == "request_password_reset_token":
            return serializers.RequestPasswordResetSerializer

        if self.action == "reset_password":
            return serializers.ResetPasswordSerializer

        if self.action == "laboratory_verify_signup":
            return serializers.LaboratoryVerifySignUpSerializer

        if self.action == "create_related_business":
            return serializers.CreateRelatedBusinessSerializer

        if self.action == "request_mobile_token":
            return serializers.MobileTokenSerializer

        if self.action == "verify_mobile_token":
            return serializers.VerifyMobileTokenSerializer

        # if self.action == "retrieve":
        #     return EmailUserDetailSerializer

        return serializers.EmailUserSerializer

    @action(detail=False, methods=["post"])
    def login(self, request, *args, **kwargs):

        queryset = self.get_queryset().filter(email__iexact=request.data["email"])

        serializer = serializers.LoginSerializer(
            data=request.data, context={"queryset": queryset}
        )
        result = serializer.is_valid(raise_exception=False)

        if result == False:
            data = {"errors": serializer.errors}
            return Response(data, status=status.HTTP_200_OK)

        user = queryset.first()

        serializer = serializers.EmailUserWithBusinessSerializer(instance=user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def laboratory_signup(self, request, *args, **kwargs):

        serializer = serializers.LaboratorySignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        serializer = serializers.EmailUserWithBusinessSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["put"])
    def laboratory_verify_signup(self, request, *args, **kwargs):

        serializer = serializers.LaboratoryVerifySignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_user = serializer.validated_data["email"]
        token_object = serializer.validated_data["token"]

        email_user.is_email_verified = True
        email_user.save()

        token_object.is_used = True
        token_object.used_time = TimeUtil.get_minutes_from_now(0)
        token_object.save()

        return Response({"message": "success"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def request_password_reset_token(self, request, *args, **kwargs):

        serializer = serializers.RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email_user = serializer.validated_data["email"]

        verification_token = EmailToken()
        verification_token.email_user = email_user
        verification_token.token = TokenUtil.get_unique_password_token(email_user)
        verification_token.expiry = TimeUtil.get_minutes_from_now(
            RESET_PASSWORD_TOKEN_EXPIRY_MINUTES
        )

        verification_token.is_token_used = False
        verification_token.category = "reset"

        verification_token.save()

        # NOTE: DO NOT SEND EMAIL VIA CELERY TASK
        EmailUtil.send_request_password_reset_email(email_user, verification_token)

        data = {"message": "token_generated"}

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def reset_password(self, request, *args, **kwargs):

        serializer = serializers.ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password_one"]
        token = serializer.validated_data["token"]

        token.is_used = True
        token.used_time = TimeUtil.get_minutes_from_now(0)
        token.save()

        email.email_user.set_password(password)
        email.email_user.save()

        data = {"message": "success"}

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def request_mobile_token(self, request, *args, **kwargs):

        serializer = serializers.MobileTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        data = {"message": "mobile_token_generated"}

        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def verify_mobile_token(self, request, *args, **kwargs):

        serializer = serializers.VerifyMobileTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        data = {"message": "mobile_token_verified"}

        return Response(data=data, status=status.HTTP_200_OK)


class RegisteredEmailUserViewset(viewsets.ModelViewSet):
    authentication_classes = CommonUtil.get_authentication_classes()

    def get_queryset(self):
        queryset = EmailUser.objects.filter(id=self.request.user.id).select_related(
            "business",
            "employer",
        )
        return queryset

    @action(detail=False, methods=["get"])
    def user_details(self, request, *args, **kwargs):

        # instance = EmailUser.objects.filter(id=request.user.id).first()
        instance = self.get_queryset().first()

        serializer = serializers.EmailUserWithBusinessSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_related_business(self, request, *args, **kwargs):

        serializer = serializers.CreateRelatedBusinessSerializer(
            data=request.data, context={"user_id": request.user.pk}
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        serializer = serializers.EmailUserWithBusinessSerializer(instance=instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def connect_related_business(self, request, *args, **kwargs):

        user = (
            EmailUser.objects.filter(id=request.user.pk)
            .select_related("business")
            .first()
        )
        serializer = serializers.ConnectRelatedBusinessSerializer(
            data=request.data, context={"user": user}
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def toggle_business_connect(self, request, *args, **kwargs):

        serializer = serializers.ToggleBusinessConnectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_business_employee(self, request, *args, **kwargs):
        user = EmailUser.objects.filter(id=request.user.pk).first()
        serializer = serializers.BusinessEmployeeSerializer(
            data=request.data, context={"user": user}
        )
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
