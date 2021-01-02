from rest_framework import serializers

from core.serializers import ServerErrorSerializer
from businesses.models import (
    Business,
    BusinessAccount,
    BusinessAddress,
    BusinessContact,
)


class BusinessAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAccount
        fields = [
            "id",
            "account_name",
            "account_number",
            "bank_name",
            "ifsc_code",
            "account_type",
            "business",
        ]


class BusinessAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = [
            "id",
            "name",
            "address",
            "city",
            "pincode",
            "address_type",
            "business",
            "state",
        ]


class BusinessContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessContact
        fields = ["id", "business", "contact", "contact_type"]


class BusinessSerializer(ServerErrorSerializer):

    contacts = BusinessContactSerializer(many=True, read_only=True)
    addresses = BusinessAddressSerializer(many=True, read_only=True)
    accounts = BusinessAccountSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "gstin",
            "category",
            "user",
            "contacts",
            "addresses",
            "accounts",
        ]
        read_only_fields = ['user']

