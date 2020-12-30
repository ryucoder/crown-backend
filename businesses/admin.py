from django.contrib import admin

from businesses.models import Business, BusinessContact, BusinessAddress, BusinessAccount, Order, OrderStatus

from core.models import State


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_filter = ["from_business", "to_business"]

    list_display = [
        "id",
        "from_business",
        "from_user",
        "to_business",
        "to_user",
        "latest_status",
        "is_urgent",
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


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):

    list_filter = ["user"]

    list_display = [
        "id",
        "name",
        "gstin",
        "user",
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
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


