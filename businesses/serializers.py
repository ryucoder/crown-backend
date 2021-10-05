from django.db import transaction
from django.db.models import Prefetch

from django.core.validators import EmailValidator

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
    BusinessOwner,
    BusinessAccount,
    BusinessAddress,
    BusinessContact,
    BusinessConnect,
    Order,
    OrderStatus,
)


class BusinessOwnerUserSerializer(serializers.ModelSerializer):
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
        ]


class BusinessOwnerSerializer(serializers.ModelSerializer):
    owner = BusinessOwnerUserSerializer(read_only=True)

    class Meta:
        model = BusinessOwner
        fields = [
            "id",
            "business",
            "owner",
            "is_active",
            "created_at",
            "modified_at",
        ]


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


class BusinessContactSerializer(ServerErrorModelSerializer):
    def validate_contact(self, contact):
        contact_type = self.initial_data.get("contact_type", None)

        if contact_type == None:
            message = "server_contact_type_none"
            raise serializers.ValidationError(message)

        if contact_type == "landline":
            length = len(str(contact).strip())

            if length < 11:
                message = "server_min_length_landline"
                raise serializers.ValidationError(message)

            if length > 11:
                message = "server_max_length_landline"
                raise serializers.ValidationError(message)

        if contact_type == "mobile":
            length = len(str(contact).strip())

            if length < 10:
                message = "server_min_length_mobile"
                raise serializers.ValidationError(message)

            if length > 10:
                message = "server_max_length_mobile"
                raise serializers.ValidationError(message)

        if contact_type == "email":
            validator = EmailValidator(message="server_invalid_email")

            try:
                validator(contact)
            except:
                message = "server_invalid_email"
                raise serializers.ValidationError(message)

        return contact

    class Meta:
        model = BusinessContact
        fields = [
            "id",
            "contact",
            "contact_type",
            "is_verified",
            "created_at",
            "modified_at",
            "business",
        ]
        read_only_fields = ["is_verified", "created_at", "modified_at", "business"]

    def create(self, validated_data):
        user = self.context["user"]

        instance = BusinessContact(**validated_data)
        instance.business = user.get_business()
        instance.is_verified = False
        instance.save()

        return instance

    def update(self, instance, validated_data):

        instance.contact = validated_data.get("contact", instance.contact)
        instance.contact_type = validated_data.get(
            "contact_type", instance.contact_type
        )
        instance.save()
        return instance


class BusinessSerializer(ServerErrorModelSerializer):

    owners = BusinessOwnerUserSerializer(many=True, read_only=True)
    contacts = BusinessContactSerializer(many=True, read_only=True)
    addresses = BusinessAddressSerializer(many=True, read_only=True)
    accounts = BusinessAccountSerializer(many=True, read_only=True)

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "gstin",
            "website",
            "category",
            "owners",
            "contacts",
            "addresses",
            "accounts",
        ]
        read_only_fields = ["owners"]


class BusinessOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "gstin",
            "website",
            "category",
            "is_active",
        ]
        read_only_fields = ["owner", "is_active"]


class OrderSerializer(ServerErrorModelSerializer):

    options = OrderOptionSerializer(read_only=True, many=True)

    options_ids = serializers.ListField(child=serializers.UUIDField(), write_only=True)

    to_laboratory_id = serializers.UUIDField(write_only=True)

    # to_user_id = serializers.UUIDField(write_only=True)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        if self.context["action"] == "update":
            for create_field in self.Meta.create_only_fields:
                self.fields.pop(create_field)

    def validate_options_ids(self, options_ids):

        queryset = OrderOption.objects.all()
        valid_ids = queryset.values_list("id", flat=True)
        option_objects = []

        for option_id in options_ids:
            if option_id not in valid_ids:
                message = "server_invalid_option_id"
                raise serializers.ValidationError(message)

            option = queryset.filter(id=option_id).first()
            option_objects.append(option)

        return option_objects

    def validate_to_laboratory_id(self, to_laboratory_id):

        # Condition 1
        queryset = Business.objects.filter(id=to_laboratory_id).prefetch_related(
            Prefetch(
                "laboratories", queryset=BusinessConnect.objects.filter(is_active=True)
            ),
        )

        if not queryset.exists():
            message = "server_absent_to_laboratory_id"
            raise serializers.ValidationError(message)

        # Condition 2
        connect_ids = queryset.first().laboratories.values_list(
            "laboratory_id", flat=True
        )

        if to_laboratory_id not in connect_ids:
            message = "server_to_laboratory_id_not_connected"
            raise serializers.ValidationError(message)

        return queryset.first()

    # def validate_to_user_id(self, to_user_id):

    #     queryset = EmailUser.objects.filter(id=to_user_id)

    #     if not queryset.exists():
    #         message = "server_absent_to_user_id"
    #         raise serializers.ValidationError(message)

    #     return queryset.first()

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
            "to_laboratory_id",
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
            "from_dentist",
            "from_user",
            "to_laboratory",
            "to_user",
        ]
        read_only_fields = [
            "from_user",
            "to_user",
            "from_dentist",
            "to_laboratory",
            "latest_status",
        ]
        create_only_fields = [
            "to_laboratory_id",
        ]

    def create(self, validated_data):
        options = validated_data.pop("options_ids")
        to_laboratory = validated_data.pop("to_laboratory_id")

        instance = Order(**validated_data)
        instance.latest_status = "pending"
        instance.to_laboratory = to_laboratory
        instance.to_user = to_laboratory.owner
        instance.from_user_id = self.context["user"].id
        instance.from_dentist = self.context["user"].get_business()

        order_status = OrderStatus()
        order_status.order = instance
        order_status.status = instance.latest_status
        order_status.user_id = self.context["user"].id

        with transaction.atomic():
            instance.save()
            instance.options.set(options)
            order_status.save()

        return instance

    def update(self, instance, validated_data):
        options = validated_data.pop("options_ids")

        instance.doctor_name = validated_data.get("doctor_name", instance.doctor_name)
        instance.patient_name = validated_data.get(
            "patient_name", instance.patient_name
        )
        instance.patient_age = validated_data.get("patient_age", instance.patient_age)
        instance.referrer = validated_data.get("referrer", instance.referrer)
        instance.delivery_date = validated_data.get(
            "delivery_date", instance.delivery_date
        )
        instance.notes = validated_data.get("notes", instance.notes)
        instance.is_urgent = validated_data.get("is_urgent", instance.is_urgent)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.teeth = validated_data.get("teeth", instance.teeth)

        with transaction.atomic():
            instance.save()
            instance.options.set(options)

        return instance


class UpdateOrderStatusSerializer(ServerErrorModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "latest_status",
        ]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):

        instance.latest_status = validated_data.get(
            "latest_status", instance.latest_status
        )

        order_status = OrderStatus()
        order_status.order = instance
        order_status.status = instance.latest_status
        order_status.user_id = self.context["user"].id

        with transaction.atomic():
            instance.save()
            order_status.save()

        return instance
