from django.contrib import admin

from core.models import City, District, State, JobType


@admin.register(City)
class CityAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
        "district",
        "created_at",
        "modified_at",
    ]

    list_per_page = 50


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "name",
        "state",
        "created_at",
        "modified_at",
    ]

    list_per_page = 50


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


@admin.register(JobType)
class OrderOptionAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "option",
        "created_at",
        "modified_at",
    ]

    list_per_page = 50
