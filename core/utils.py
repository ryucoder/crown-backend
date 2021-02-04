from pprint import pprint

from django.conf import settings

from django.core.paginator import Paginator
from django.core.paginator import InvalidPage

from rest_framework import pagination
from rest_framework.response import Response

from sendgrid.sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from sentry_sdk import capture_exception


class CurrentPagePagination(pagination.PageNumberPagination):
    page_size = 8
    invalid_page_message = "server_invalid_page_number"

    def get_paginated_response(self, data):
        return Response(
            {
                "items_per_page": self.page_size,
                "current_page": self.page.number,
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "results": data,
            }
        )


class EmailUtil:
    @staticmethod
    def send_signup_email(instance, verification_token):

        verify_url = settings.DOMAIN_NAME + "/#/signup/verify?"

        verify_url += (
            "email="
            + str(instance.email)
            + "&"
            + "token="
            + str(verification_token.token)
        )

        message = Mail(
            from_email="rockstar.ryucoder@gmail.com",
            to_emails=instance.email,
        )

        message.dynamic_template_data = {"verify_url": verify_url}

        # NOTE: DYNAMIC TEMPLATE ID OF THE TEMPLATE IN THE SENDGRID ACCOUNT for Sign Up email
        message.template_id = settings.SENDGRID_TEMPLATE_ID_LABORATORY_SIGNUP_EMAIL

        try:
            sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sendgrid_client.send(message)

        except Exception as error:
            # log to sentry
            capture_exception(error)

    @staticmethod
    def send_request_password_reset_email(instance, verification_token):

        verify_url = settings.DOMAIN_NAME + "/#/password/reset?"

        verify_url += (
            "email="
            + str(instance.email)
            + "&"
            + "token="
            + str(verification_token.token)
        )

        message = Mail(
            from_email="info@packfect.com",
            to_emails=instance.email,
        )

        message.dynamic_template_data = {"verify_url": verify_url}

        # NOTE: DYNAMIC TEMPLATE ID OF THE TEMPLATE IN THE RESET PASSWORD email
        message.template_id = settings.SENDGRID_TEMPLATE_ID_LABORATORY_SIGNUP_EMAIL

        try:
            sendgrid_client = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sendgrid_client.send(message)

        except Exception as error:
            # log to sentry
            capture_exception(error)
