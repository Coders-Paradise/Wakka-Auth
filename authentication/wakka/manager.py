from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone


class SoftDeleteQuerySet(QuerySet):
    def delete(self) -> tuple[int, dict[str, int]]:
        deleted_at = timezone.now()
        return super().update(deleted_at=deleted_at, is_active=False), {"deleted": 1}


class AppManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )

    def include_deleted(self) -> QuerySet:
        return super().get_queryset()


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        from .models import Application

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        app = Application.objects.get_or_create(
            app_name="administration", title="Administration"
        )[0]
        extra_fields.setdefault("app", app)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_at__isnull=True
        )

    def include_deleted(self) -> QuerySet:
        return super().get_queryset()
