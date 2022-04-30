from django.contrib import admin

from businesses.models import (
    Business,
    BusinessOwner,
    BusinessEmployee,
    BusinessContact,
    BusinessConnect,
    BusinessAddress,
    BusinessAccount,
    Order,
    OrderStatus,
)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_filter = [
        "is_urgent",
        "is_active",
        "latest_status",
    ]

    list_display = [
        "id",
        "from_business",
        "from_user",
        "to_business",
        "to_user",
        "latest_status",
        "is_urgent",
        "is_active",
        "delivery_date",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):

    list_filter = ["order", "user"]

    list_display = [
        "id",
        "order",
        "status",
        "user",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(BusinessConnect)
class BusinessConnectAdmin(admin.ModelAdmin):

    list_filter = ["is_active"]

    list_display = [
        "id",
        "dentist",
        "laboratory",
        "is_active",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(BusinessOwner)
class BusinessOwnerAdmin(admin.ModelAdmin):

    list_filter = ["is_active"]

    list_display = [
        "id",
        "business",
        "owner",
        "is_active",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):

    list_filter = [
        "category",
        "is_active",
    ]

    list_display = [
        "id",
        "name",
        "gstin",
        "website",
        "category",
        "is_active",
        "referral",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(BusinessEmployee)
class BusinessEmployeeAdmin(admin.ModelAdmin):

    list_filter = ["business"]

    list_display = [
        "id",
        "business",
        "employee",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(BusinessContact)
class BusinessContactAdmin(admin.ModelAdmin):

    list_filter = ["business", "contact_type"]

    list_display = [
        "id",
        "business",
        "contact",
        "contact_type",
        "is_verified",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(BusinessAddress)
class BusinessAddressAdmin(admin.ModelAdmin):

    search_fields = ["id" "pincode", "address_type", "user__id"]

    list_filter = ["address_type"]

    list_display = [
        "id",
        "name",
        "city",
        "state",
        "pincode",
        "address_type",
        "business",
        "is_default",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(BusinessAccount)
class BusinessAccountAdmin(admin.ModelAdmin):

    search_fields = ["id"]

    list_filters = ["account_type"]

    list_display = [
        "id",
        "account_name",
        "account_number",
        "bank_name",
        "ifsc_code",
        "account_type",
        "is_default",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25
