import uuid

from users.models import PasswordToken


class PasswordUtil:
    @staticmethod
    def get_unique_password_token(email_user):

        unique_found = False
        all_tokens = PasswordToken.objects.filter(email_user=email_user).values_list(
            "token", flat=True
        )

        while not unique_found:
            current_token = uuid.uuid4()

            if current_token not in all_tokens:
                unique_found = True

        return current_token
