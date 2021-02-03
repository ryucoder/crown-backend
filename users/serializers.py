from rest_framework import serializers

from users.models import EmailUser

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
                self.fields["owners_business"] = BusinessOnlySerializer(instance=self.instance.employer.business)

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
