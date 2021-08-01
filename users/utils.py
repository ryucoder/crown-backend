import uuid
import random

from users.models import EmailToken


class TokenUtil:
    @staticmethod
    def get_unique_password_token(email_user):

        unique_found = False
        all_tokens = EmailToken.objects.filter(email_user=email_user).values_list(
            "token", flat=True
        )

        while not unique_found:
            current_token = uuid.uuid4()

            if current_token not in all_tokens:
                unique_found = True

        return current_token

    @staticmethod
    def get_mobile_token():
        mobile_token = str(random.randint(100000, 999999))
        return mobile_token
