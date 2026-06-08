from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "is_premium", "is_staff", "created_at")
    list_filter = ("is_premium", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("-created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "UPSC Profile",
            {
                "fields": (
                    "phone_number",
                    "is_premium",
                    "bio",
                    "preparation_year",
                    "optional_subject",
                    "avatar",
                )
            },
        ),
    )
