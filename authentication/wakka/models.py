from uuid import uuid4
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)

from .manager import UserManager


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=40)
    app_name = models.CharField(max_length=40, unique=True)

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
