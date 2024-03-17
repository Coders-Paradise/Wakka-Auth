from typing import Any, Mapping

from django.contrib.auth.models import update_last_login
from django.core.mail import EmailMessage
from django.db import connection
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken

from .constants import ONE_TIME_TOKEN_EXPIRY, OneTimeTokenType
from .exceptions import (
    ForgotPasswordEmailSendingFailedException,
    InvalidAppNameException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
    OneTimeTokenInvalidException,
    UserAlreadyExistsException,
    UserDoesNotExistException,
    UserNotActiveException,
    UserNotVerifiedException,
    VerificationEmailSendingFailedException,
)
from .models import Application, User
from .utils import OneTimeJWTToken


class AuthService:
    @classmethod
    def health_check(cls) -> Mapping[str, bool]:
        conn = False
        try:
            User.objects.count()
            conn = True
        except Exception as e:
            pass
        status = {
            "database": conn,
            "server": True,
        }
        return status

    @classmethod
    def get_user_by_id(cls, user_id: str) -> User:
        user = User.objects.filter(id=user_id).first()
        if user:
            return user
        raise UserDoesNotExistException

    @classmethod
    def get_user_by_email(
        cls, email: str = None, app: Application = None, raise_exception: bool = False
    ) -> User:
        """Get user by email and app. If user does not exist, return None."""
        user = User.objects.filter(email=email, app=app).first()
        # The exception is not raised by default, because in such cases,
        # the client does not need to know if the user exists or not.
        if raise_exception and not user:
            raise UserDoesNotExistException
        return user

    @classmethod
    def get_user_by_email_password(
        cls,
        email: str = None,
        password: str = None,
        app: Application = None,
    ) -> User:
        """Get user by email and password. If user does not exist, raise InvalidCredentialsException."""
        user = cls.get_user_by_email(email=email, app=app)
        if user and user.check_password(password):
            return user
        raise InvalidCredentialsException

    @classmethod
    def check_user_verification_status(
        cls, user: User = None, raise_exception: bool = False
    ) -> bool:
        if user and user.verified:
            return True
        if raise_exception:
            raise UserNotVerifiedException
        return False

    @classmethod
    def check_user_active_status(
        cls, user: User = None, raise_exception: bool = False
    ) -> bool:
        if user and user.is_active:
            return True
        if raise_exception:
            raise UserNotActiveException
        return False

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
        cls.check_user_verification_status(user=user, raise_exception=True)
        cls.check_user_active_status(user=user, raise_exception=True)

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
            try:
                refresh_token = RefreshToken(refresh_token)
                refresh_token.verify()
            except Exception as e:
                raise InvalidRefreshTokenException
            user = User.objects.get(id=refresh_token.get("user_id"))
            cls.check_user_verification_status(user=user, raise_exception=True)
            cls.check_user_active_status(user=user, raise_exception=True)
            access_token = refresh_token.access_token
            # Updating the last login time
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

    @classmethod
    def update_user(cls, user_id: str, **validated_data) -> User:
        user = cls.get_user_by_id(user_id)
        cls.check_user_verification_status(user=user, raise_exception=True)
        for key, value in validated_data.items():
            setattr(user, key, value)
        user.save()
        return user

    @classmethod
    def delete_user(cls, user_id: str) -> None:
        user = User.objects.filter(id=user_id).first()
        if user:
            user.delete()
        raise UserDoesNotExistException

    @classmethod
    def send_verification_email(
        cls,
        user: User = None,
        app: Application = None,
        domain: str = None,
        protocol: str = None,
    ) -> None:
        mail_subject = "Activate your account"
        token = cls.generate_one_time_verification_token(
            user=user, type=OneTimeTokenType.EMAIL_VERIFICATION.value
        )
        verify_url = f"{protocol}://{domain}/one-time/verify-email/?token={token}"
        message = render_to_string(
            "email_verification_mail.html",
            {"user": user, "verify_url": verify_url, "app": app},
        )

        email = EmailMessage(subject=mail_subject, body=message, to=[user.email])
        email.content_subtype = "html"
        try:
            email.send()
        except Exception as e:
            print(e.__traceback__)
            raise VerificationEmailSendingFailedException

    @classmethod
    def validate_email_verification_token(cls, token: str) -> None:
        if not token:
            raise OneTimeTokenInvalidException
        try:
            payload = OneTimeJWTToken.verify(token)
            if payload["type"] != OneTimeTokenType.EMAIL_VERIFICATION.value:
                raise OneTimeTokenInvalidException
            user = cls.get_user_by_id(payload.get("user_id"))
            # set user as verified and active once the email is verified
            user.is_active = True
            user.verified = True
            user.save()
        except Exception as e:
            raise e

    @classmethod
    def send_forgot_password_email(
        cls,
        user: User = None,
        app: Application = None,
        domain: str = None,
        protocol: str = None,
    ) -> None:
        mail_subject = "Reset your Password"
        token = cls.generate_one_time_verification_token(
            user=user, type=OneTimeTokenType.FOROGT_PASSWORD.value
        )
        reset_url = f"{protocol}://{domain}/one-time/forgot-password/?token={token}"
        message = render_to_string(
            "forgot_password_mail.html",
            {"user": user, "reset_url": reset_url, "app": app},
        )

        email = EmailMessage(subject=mail_subject, body=message, to=[user.email])
        email.content_subtype = "html"
        try:
            email.send()
        except Exception as e:
            print(e.__traceback__)
            raise ForgotPasswordEmailSendingFailedException

    @classmethod
    def validate_forgot_password_token(cls, token: str) -> Mapping[str, Any]:
        if not token:
            raise OneTimeTokenInvalidException
        try:
            payload = OneTimeJWTToken.verify(token)
            if payload["type"] != OneTimeTokenType.FOROGT_PASSWORD.value:
                raise OneTimeTokenInvalidException
            return payload
        except Exception as e:
            raise e

    @classmethod
    def generate_one_time_verification_token(
        cls, user: User = None, type: str = None
    ) -> str:
        token = OneTimeJWTToken.obtain(
            payload={
                "user_id": str(user.pk),
                "app_id": str(user.app.pk),
                "type": type,
            },
            lifetime=ONE_TIME_TOKEN_EXPIRY,
        )
        return token

    @classmethod
    def change_password(cls, user: User = None, password: str = None) -> None:
        user.set_password(password)
        user.save()
