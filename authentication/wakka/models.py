from typing import Iterable
from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.management.utils import get_random_secret_key
from django.db import models

from .manager import UserManager


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=40)
    app_name = models.CharField(
        max_length=40,
        unique=True,
        help_text="Unique name for the application. Contains lowercase letters, numbers, and underscores. No spaces allowed.",
    )
    server_api_key = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Copy this key to the target application. Set this field to null once you copied the key using Actions.",
    )
    server_api_key_hash = models.CharField(max_length=255, blank=True)

    def regenerate_server_api_key(self):
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

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.server_api_key_hash:
            self.server_api_key = get_random_secret_key()
            self.server_api_key_hash = make_password(self.server_api_key)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title}: {self.app_name}"


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(null=False, blank=False)
    username = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=40, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    app = models.ForeignKey(Application, on_delete=models.CASCADE)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    objects = UserManager()

    def __str__(self):
        return f"<{self.name}: {self.email}>"

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name
