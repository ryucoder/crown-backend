from django.db import transaction

from rest_framework import serializers

from core.serializers import (
    ServerErrorSerializer,
    ServerErrorModelSerializer,
    OrderOptionSerializer,
)
from core.models import OrderOption, State

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
            "is_default",
            "business",
        ]
        read_only_fields = ["business"]

    def create(self, validated_data):
        user = validated_data.pop("user")

        instance = BusinessAccount(**validated_data)
        instance.business = user.get_business()
        instance.save()

        is_default = validated_data["is_default"]

        if is_default:
            queryset = user.get_business().accounts.exclude(id=instance.id)
            queryset.update(is_default=False)

        return instance

    def update(self, instance, validated_data):

        instance.account_name = validated_data.get(
            "account_name", instance.account_name
        )
        instance.account_number = validated_data.get(
            "account_number", instance.account_number
        )
        instance.bank_name = validated_data.get("bank_name", instance.bank_name)
        instance.ifsc_code = validated_data.get("ifsc_code", instance.ifsc_code)
        instance.account_type = validated_data.get(
            "account_type", instance.account_type
        )
        instance.is_default = validated_data.get("is_default", instance.is_default)
        instance.save()

        is_default = validated_data["is_default"]

        if is_default:
            queryset = BusinessAccount.objects.filter(
                business_id=instance.business_id
            ).exclude(id=instance.id)
            queryset.update(is_default=False)

        return instance


class BusinessAddressSerializer(ServerErrorModelSerializer):
    state_id = serializers.UUIDField(write_only=True)

    def validate_state_id(self, state_id):
        queryset = State.objects.filter(id=state_id)

        if not queryset.exists():
            message = "server_absent"
            raise serializers.ValidationError(message)

        return queryset.first()

    def validate_address_type(self, address_type):
        all_addresses = self.context["user"].get_business().addresses.all()

        if all_addresses.count() == 0 and address_type != "headquarters":
            message = "server_headquarter_must_exist"
            raise serializers.ValidationError(message)

        queryset = all_addresses.filter(address_type="headquarters")

        if address_type == "headquarters" and queryset.exists():
            message = "server_headquarter_already_exists"
            raise serializers.ValidationError(message)

        return address_type

    class Meta:
        model = BusinessAddress
        fields = [
            "state_id",
            "id",
            "name",
            "address",
            "city",
            "pincode",
            "address_type",
            "business",
            "state",
            "is_default",
            "created_at",
            "modified_at",
        ]
        read_only_fields = ["business", "state", "created_at", "modified_at"]

    def create(self, validated_data):
        user = self.context["user"]
        state = validated_data.pop("state_id")

        is_default = validated_data["is_default"]
        is_default = is_default if user.get_business().addresses.count() > 0 else True

        instance = BusinessAddress(**validated_data)
        instance.business = user.get_business()
        instance.state = state
        instance.is_default = is_default
        instance.save()

        if is_default:
            queryset = user.get_business().addresses.exclude(id=instance.id)
            queryset.update(is_default=False)

        return instance

    def update(self, instance, validated_data):

        instance.name = validated_data.get("name", instance.name)
        instance.address = validated_data.get("address", instance.address)
        instance.city = validated_data.get("city", instance.city)
        instance.pincode = validated_data.get("pincode", instance.pincode)
        instance.address_type = validated_data.get(
            "address_type", instance.address_type
        )
        instance.state = validated_data.get("state_id", instance.state)
        instance.is_default = validated_data.get("is_default", instance.is_default)
        instance.save()

        is_default = validated_data["is_default"]

        if is_default:
            queryset = BusinessAddress.objects.filter(
                business_id=instance.business_id
            ).exclude(id=instance.id)
            queryset.update(is_default=False)

        return instance


class ToggleDefaultBusinessAddressSerializer(ServerErrorModelSerializer):
    class Meta:
        model = BusinessAddress
        fields = [
            "id",
            "is_default",
        ]
        read_only_fields = ["is_default"]

    def update(self, instance, validated_data):

        instance.is_default = True if instance.is_default == False else False

        all_other_addresses = BusinessAddress.objects.filter(
            business_id=instance.business_id
        ).exclude(id=instance.id)

        with transaction.atomic():
            instance.save()
            all_other_addresses.update(is_default=False)

        return instance


class BusinessContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessContact
        fields = ["id", "business", "contact", "contact_type"]

    def create(self, validated_data):
        user = self.context["user"]
        state = validated_data.pop("state_id")

        is_default = validated_data["is_default"]
        is_default = is_default if user.get_business().addresses.count() > 0 else True

        instance = BusinessAddress(**validated_data)
        instance.business = user.get_business()
        instance.state = state
        instance.is_default = is_default
        instance.save()

        if is_default:
            queryset = user.get_business().addresses.exclude(id=instance.id)
            queryset.update(is_default=False)

        return instance

    def update(self, instance, validated_data):

        instance.name = validated_data.get("name", instance.name)
        instance.address = validated_data.get("address", instance.address)
        instance.city = validated_data.get("city", instance.city)
        instance.pincode = validated_data.get("pincode", instance.pincode)
        instance.address_type = validated_data.get(
            "address_type", instance.address_type
        )
        instance.state = validated_data.get("state_id", instance.state)
        instance.is_default = validated_data.get("is_default", instance.is_default)
        instance.save()

        is_default = validated_data["is_default"]

        if is_default:
            queryset = BusinessAddress.objects.filter(
                business_id=instance.business_id
            ).exclude(id=instance.id)
            queryset.update(is_default=False)

        return instance


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

    options_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True)

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

    def validate_teeth(self, teeth):

        length = len(teeth.keys())

        if length < 1:
            message = "server_teeth_min"
            raise serializers.ValidationError(message)

        if length > 32:
            message = "server_teeth_max"
            raise serializers.ValidationError(message)

        teeth_key_range = [str(item) for item in range(1, 9)]

        for key, value in teeth.items():

            if key[0] not in ["u", "l"]:
                message = "server_invalid_key_start"
                raise serializers.ValidationError(message)

            if key[1] not in ["l", "r"]:
                message = "server_invalid_key_side"
                raise serializers.ValidationError(message)

            if key[3] not in teeth_key_range:
                message = "server_invalid_key_end"
                raise serializers.ValidationError(message)

            if value != True:
                message = "server_invalid_value"
                raise serializers.ValidationError(message)

        return teeth

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
        read_only_fields = [
            "from_user",
            "to_user",
            "from_business",
            "to_business",
            "latest_status",
        ]

    def create(self, validated_data):
        options_ids = validated_data.pop("options_ids")
        to_business = validated_data.pop("to_business_id")
        from_user_id = validated_data.pop("from_user_id")

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
