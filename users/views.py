from users import serializers
from users.models import EmailUser

from rest_framework.mixins import RetrieveModelMixin
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action


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
        return EmailUser.objects.all()

    def get_serializer_class(self):

        if self.action == "login":
            return serializers.LoginSerializer

        # if self.action == "client_signup_view":
        #     return ClientSignUpSerializer

        # if self.action == "request_reset_password":
        #     return RequestResetPasswordSerializer

        # if self.action == "reset_password":
        #     return ResetPasswordSerializer

        # if self.action == "request_mobile_token":
        #     return MobileTokenSerializer

        # if self.action == "retrieve":
        #     return EmailUserDetailSerializer

        return serializers.EmailUserSerializer

    @action(detail=False, methods=["post"])
    def login(self, request, *args, **kwargs):

        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        serializer = serializers.EmailUserSerializer(instance=user)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["post"])
    # def client_signup(self, request, *args, **kwargs):

    #     serializer = ClientSignUpSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     instance = serializer.save()

    #     serializer = EmailUserSerializer(instance=instance)

    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=False, methods=["put"])
    # def client_verify_signup(self, request, *args, **kwargs):

    #     serializer = ClientVerifySignUpSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     email_user = serializer.validated_data["email"]
    #     token_object = serializer.validated_data["token"]

    #     email_user.is_email_verified = True
    #     email_user.save()

    #     token_object.is_used = True
    #     token_object.save()

    #     return Response({"message": "success"}, status=status.HTTP_201_CREATED)

    # @action(detail=False, methods=["post"])
    # def request_password_reset_token(self, request, *args, **kwargs):

    #     serializer = RequestResetPasswordSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     email_user = serializer.validated_data["email"]

    #     verification_token = ResetPasswordToken()
    #     verification_token.email_user = email_user
    #     verification_token.token = EmailUserUtil.get_password_reset_token(email_user)
    #     verification_token.expiry = timezone.now() + RESET_PASSWORD_TOKEN_EXPIRY_TIME
    #     verification_token.is_token_used = False

    #     verification_token.save()

    #     # send email to user via celery task
    #     EmailUtil.send_request_password_reset_email(email_user, verification_token)

    #     data = {"message": "token_generated"}

    #     return Response(data=data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["post"])
    # def reset_password(self, request, *args, **kwargs):

    #     serializer = ResetPasswordSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     email = serializer.validated_data["email"]
    #     password = serializer.validated_data["password_one"]
    #     token = serializer.validated_data["token"]

    #     token.is_used = True
    #     token.save()

    #     email.email_user.set_password(password)
    #     email.email_user.save()

    #     data = {"message": "passsword_reset_successfully"}

    #     return Response(data=data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["post"])
    # def request_mobile_token(self, request, *args, **kwargs):

    #     serializer = MobileTokenSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)

    #     instance = serializer.save()

    #     data = {"message": "mobile_token_generated"}

    #     return Response(data=data, status=status.HTTP_200_OK)

