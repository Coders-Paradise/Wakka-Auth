from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from .models import Application, User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = (
        "username",
        "name",
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("username", "name","email", "password", "app")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "name",
                    "password1",
                    "password2",
                    "app",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

    def delete_queryset(self, request: HttpRequest, queryset: QuerySet[User]) -> None:
        for obj in queryset:
            obj.delete()
        return super().delete_queryset(request, queryset)


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("app_name", "title")
    search_fields = ("app_name", "title")
    ordering = ("app_name",)
    fields = ("title", "app_name", "server_api_key")
    readonly_fields = ("server_api_key",)
    actions = ["nullify_server_api_key", "regenerate_api_key"]

    def nullify_server_api_key(self, request, queryset: QuerySet[Application]):
        for obj in queryset:
            obj.nullify_server_api_key()
        self.message_user(
            request, "Server API key set to null for selected applications."
        )

    nullify_server_api_key.short_description = (
        "Nullify server API key for selected applications"
    )

    def regenerate_api_key(self, request, queryset: QuerySet[Application]):
        for obj in queryset:
            obj.regenerate_server_api_key()
        self.message_user(
            request, "Server API key regenerated for selected applications."
        )

    regenerate_api_key.short_description = (
        "Regenerate server API key for selected applications"
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Application, ApplicationAdmin)
