from django.contrib import admin
from django.contrib.auth.hashers import make_password

from django.utils import timezone

from users.forms import EmailUserForm


admin.site.site_header = "Crown Admin Panel"


from users.models import (
    EmailUser,
    PasswordToken,
    MobileToken,
)


@admin.register(MobileToken)
class MobileTokenAdmin(admin.ModelAdmin):
    def is_expired(self, obj):
        return timezone.now() > obj.expiry

    search_fields = ["id", "mobile", "token"]

    list_filter = ["is_used"]

    list_display = [
        "id",
        "mobile",
        "token",
        "expiry",
        "is_expired",
        "is_used",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25


@admin.register(PasswordToken)
class PasswordTokenAdmin(admin.ModelAdmin):
    def is_expired(self, obj):
        return timezone.now() > obj.expiry

    search_fields = ["id", "token"]

    list_filter = ["category", "is_used"]

    list_display = [
        "id",
        "email_user",
        "token",
        "category",
        "is_used",
        "is_expired",
        "expiry",
        "created_at",
        "modified_at",
    ]

    class Meta:
        model = PasswordToken

    list_per_page = 25


@admin.register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):

    form = EmailUserForm

    search_fields = ["id", "first_name", "last_name", "email"]

    list_display_links = ["email"]

    list_filter = ["user_type", "is_active", "is_staff", "is_superuser"]

    #  For job list view
    list_display = [
        "id",
        "email",
        "is_email_verified",
        "first_name",
        "last_name",
        "mobile",
        "is_mobile_verified",
        "user_type",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "modified_at",
    ]

    list_per_page = 25

    #  For job detail view
    fieldsets = [
        ("Login Details", {"fields": ("email", "password")}),
        (
            "Personal Details",
            {
                # 'classes': ('collapse',),
                "fields": ("first_name", "last_name", "mobile",),
            },
        ),
        (
            "User Status",
            {
                "fields": (
                    "user_type",
                    "is_email_verified",
                    "is_mobile_verified",
                    "mobile_verified_time",
                )
            },
        ),
        ("Groups", {"fields": ("groups",)}),
        ("Permissions", {"fields": ("user_permissions",)}),
        ("Account Status", {"fields": ("is_active", "is_staff", "is_superuser")},),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    ]

    # Admin should not be able to modify these fields
    readonly_fields = [
        "mobile_verified_time",
        "last_login",
        "date_joined",
    ]

    def save_model(self, request, obj, form, change):
        """
            As the password needs to be hashed before it is saved to database,
            we need to override this method to achieve that.

            If we don't do this, password will be saved in the plain text format.
        """

        # If password is not hashed, hash it.
        # If we hash it everytime without checking, hashed password will also be hashed, lolz

        # This code will break if the default hasher is different than pbkdf2_sha256
        # This code will also break if the user entered password starts with pbkdf2_sha256, lolz

        # I wish there was a better and scalable way to know if the password is hashed or not

        if self._is_password_hashed(obj):
            obj.password = make_password(obj.password)

        obj.save()

    def _is_password_hashed(self, obj):
        """
            A separate function is created here,
            so if you want to support multiple different hashers,
            you can just add one extra if condition in this function,
            so that the above code need not be updated at all.
        """

        if obj.password.startswith("pbkdf2_sha256"):
            return False

        return True

    class Meta:
        model = EmailUser
