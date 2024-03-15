from django.contrib.auth.models import update_last_login
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .constants import ACCESS_TOKEN_NAME, REFRESH_TOKEN_NAME
from .exceptions import (
    InvalidAppNameException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
    UserAlreadyExistsException,
    UserDoesNotExistException,
)
from .models import Application, User
from .serializers import TokenPairRequestSeralizer, TokenRefreshRequestSerializer


class AuthService:

    @classmethod
    def get_user_by_id(cls, user_id: str) -> User:
        user = User.objects.filter(id=user_id).first()
        if user:
            return user
        raise UserDoesNotExistException

    @classmethod
    def get_user_by_email_password(
        cls,
        email: str = None,
        password: str = None,
        app: Application = None,
    ) -> User:
        user = User.objects.filter(email=email, app=app).first()
        if user and user.check_password(password):
            return user
        raise InvalidCredentialsException

    @classmethod
    def get_token_pair(
        cls,
        email: str = None,
        password: str = None,
        app: Application = None,
    ) -> dict:
        user = cls.get_user_by_email_password(
            email=email,
            password=password,
            app=app,
        )

        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["name"] = user.name
        refresh["app"] = user.app.app_name
        update_last_login(None, user)

        return {
            "refresh_token": str(refresh),
            "access_token": str(refresh.access_token),
        }

    @classmethod
    def get_access_token(cls, refresh_token: str = None) -> dict:
        if refresh_token:
            refresh_token = RefreshToken(refresh_token)
            refresh_token.verify()
            access_token = refresh_token.access_token
            # Updating the last login time
            user = User.objects.get(id=access_token.get("user_id"))
            update_last_login(None, user=user)
            return {"access_token": str(access_token)}
        raise InvalidRefreshTokenException

    @classmethod
    def create_user(
        cls,
        email: str = None,
        password: str = None,
        name: str = None,
        app: Application = None,
        **extra_fields,
    ) -> User:
        user = User.objects.include_deleted().filter(email=email, app=app)
        """
        Checks if user already exists.
        Case 1: User exists but soft deleted -> Hard delete the user and create a new user
        Case 2: User exists but not soft deleted -> Raise UserAlreadyExistsException
        """
        if user.exists():
            user = user.first()
            if user.deleted_at:  # Case 1
                user.hard_delete()
            else:
                raise UserAlreadyExistsException

        user = User.objects.create_user(
            email=email,
            password=password,
            app=app,
            name=name,
            **extra_fields,
        )
        return user

    def update_user(self, user_id: str, **validated_data) -> User:
        user = User.objects.get(id=user_id)
        for key, value in validated_data.items():
            setattr(user, key, value)
        user.save()
        return user

    def delete_user(self, user_id: str) -> None:
        user = User.objects.filter(id=user_id).first()
        if user:
            user.delete()
        raise UserDoesNotExistException
