from django.contrib import admin

from core.models import State, OrderOption


@admin.register(State)
class StateAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
        "gst_code",
        "created_at",
        "modified_at",
    ]

    list_per_page = 50


@admin.register(OrderOption)
class OrderOptionAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "option",
        "created_at",
        "modified_at",
    ]

    list_per_page = 50
