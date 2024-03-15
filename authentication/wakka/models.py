from typing import Iterable
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.management.utils import get_random_secret_key
from django.db import models
from django.utils import timezone

from .manager import AppManager, UserManager


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=40)
    deleted_at = models.DateTimeField(null=True, blank=True)
    app_name = models.CharField(
        max_length=40,
        unique=True,
        help_text="Unique name for the application. Contains lowercase letters, numbers, and underscores. No spaces allowed.",
    )  # app name should always contain lowercase letters, numbers, and underscores
    server_api_key = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Copy this key to the target application. Set this field to null once you copied the key using Actions.",
    )
    server_api_key_hash = models.CharField(max_length=255, blank=True)
    objects = AppManager()

    def generate_server_api_key(self):
        self.server_api_key = get_random_secret_key()
        self.server_api_key_hash = make_password(self.server_api_key)
        self.save()

    def nullify_server_api_key(self):
        self.server_api_key = None
        self.save()

    def clean(self):
        if not self.app_name.islower():
            raise ValidationError("App name must be in lowercase")
        if not self.app_name.isalnum():
            raise ValidationError("App name must contain only letters and numbers")
        if " " in self.app_name:
            raise ValidationError("App name must not contain spaces")
        return super().clean()

    def delete(self) -> tuple[int, dict[str, int]]:
        self.app_name = f"{self.app_name}$$deleted"
        self.deleted_at = timezone.now()

    def save(self, *args, **kwargs):
        self.full_clean()
        # If the hash is empty, generate a new server api key, hash pair
        if not self.server_api_key_hash:
            self.generate_server_api_key()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}: {self.app_name}"


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(null=False, blank=False)
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=40, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return f"<{self.name}: {self.email}>"

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def delete(self) -> tuple[int, dict[str, int]]:
        self.is_active = False
        self.username = f"{self.username}$$deleted"
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self) -> tuple[int, dict[str, int]]:
        return super().delete()

    def save(self, *args, **kwargs):

        if not self.username:
            # If the username is empty, set a new username like instagram$$johndoe@test.com
            username = f"{self.app.app_name}$${self.email}".lower()
            self.username = username
        return super().save(*args, **kwargs)
