from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import Application, User
from django.db.models.query import QuerySet


class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = User
    list_display = (
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
        (None, {"fields": ("username", "email", "password", "app")}),
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


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("app_name", "title")
    search_fields = ("app_name", "title")
    ordering = ("app_name",)
    readonly_fields = (
        "server_api_key",
        "server_api_key_hash",
    )
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
