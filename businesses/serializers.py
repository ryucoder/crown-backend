from django.db import transaction

from rest_framework import serializers

from core.serializers import ServerErrorSerializer, OrderOptionSerializer
from core.models import OrderOption

from users.models import EmailUser

from businesses.models import (
    Business,
    BusinessAccount,
    BusinessAddress,
    BusinessContact,
    Order,
    OrderStatus,
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
            "owner",
            "contacts",
            "addresses",
            "accounts",
        ]
        read_only_fields = ["owner"]


class BusinessOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "gstin",
            "category",
            "owner",
        ]
        read_only_fields = ["owner"]


class OrderSerializer(serializers.ModelSerializer):

    options = OrderOptionSerializer(read_only=True, many=True)

    options_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True
    )

    to_business_id = serializers.UUIDField(write_only=True)

    # to_user_id = serializers.UUIDField(write_only=True)
    # def validate_to_user_id(self, to_user_id):
        
    #     queryset = EmailUser.objects.filter(id=to_user_id)

    #     if not queryset.exists():
    #         message = "server_absent_to_user_id"
    #         raise serializers.ValidationError(message)

    #     return queryset.first() 

    def validate_to_business_id(self, to_business_id):
        
        queryset = Business.objects.filter(id=to_business_id)

        if not queryset.exists():
            message = "server_absent_to_business_id"
            raise serializers.ValidationError(message)

        return queryset.first() 

    def validate_options_ids(self, options_ids):
        
        valid_ids = OrderOption.objects.values_list("id", flat=True)

        for option_id in options_ids:
            if option_id not in valid_ids:
                message = "server_invalid_option_id"
                raise serializers.ValidationError(message)

        return options_ids 

    class Meta:
        model = Order
        fields = [
            # "to_user_id",
            "to_business_id",
            "options_ids",
            "id",
            "doctor_name",
            "patient_name",
            "patient_age",
            "referrer",
            "delivery_date",
            "notes",
            "options",
            "is_urgent",
            "is_active",
            "teeth",
            "latest_status",
            "from_business",
            "from_user",
            "to_business",
            "to_user",
        ]
        read_only_fields = ["from_user", "to_user", "from_business", "to_business", "latest_status"]


    def create(self, validated_data):
        options_ids = validated_data.pop("options_ids")
        # write_teeth = validated_data.pop("write_teeth")
        # to_user = validated_data.pop("to_user_id")
        to_business = validated_data.pop("to_business_id")
        from_user_id = validated_data.pop("from_user_id")

        # from_user_id = "743b88f4-5a42-44e2-8187-c43e1be49d1a"
        print()
        print()
        print("from_user_id")
        print(from_user_id)
        print()
        print()
        options = OrderOption.objects.filter(id__in=options_ids)


        instance = Order(**validated_data)
        instance.latest_status = "pending"
        instance.to_business = to_business
        instance.to_user = to_business.owner
        instance.from_user_id = from_user_id
        instance.from_business = EmailUser.objects.get(id=from_user_id).get_business()

        order_status = OrderStatus()
        order_status.order = instance 
        order_status.status = instance.latest_status
        order_status.user_id = from_user_id

        with transaction.atomic():
            instance.save()
            instance.options.set(options)
            order_status.save()

        return instance