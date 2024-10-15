import datetime
from typing import Any, Mapping
from uuid import uuid4

import jwt
from django.conf import settings
from django.utils import timezone

from .constants import AuthTokenType
from .exceptions import OneTimeTokenExpiredException, OneTimeTokenInvalidException
from .models import OnetimeTokenRecords, User


class OneTimeJWTToken:
    """Generating and verifying one time jwt tokens for email verification and password reset"""

    signing_key = settings.JWT_SETTINGS["SIGNING_KEY"]
    verifying_key = settings.JWT_SETTINGS["VERIFYING_KEY"]
    algorithm = settings.JWT_SETTINGS["ALGORITHM"]
    issuer = settings.JWT_SETTINGS["ISSUER"]
    token_lifetime = settings.JWT_SETTINGS["ONE_TIME_TOKEN_LIFETIME"]

    @classmethod
    def obtain(cls, payload: dict) -> str:
        """Generate a one time jwt token"""
        jti = uuid4().hex
        expires_at = timezone.now() + cls.token_lifetime
        token = jwt.encode(
            payload={"iss": cls.issuer, "jti": jti, "exp": expires_at, **payload},
            key=cls.signing_key,
            algorithm=cls.algorithm,
        )
        token_record = OnetimeTokenRecords(jti=jti, expires_at=expires_at)
        token_record.save()
        return token

    @classmethod
    def verify(cls, token: str) -> Mapping[str, Any]:
        """Verify a one time jwt token"""
        try:
            payload = jwt.decode(
                jwt=token, key=cls.verifying_key, algorithms=[cls.algorithm]
            )
        except jwt.ExpiredSignatureError:
            raise OneTimeTokenExpiredException
        except jwt.InvalidIssuerError:
            raise OneTimeTokenInvalidException

        jti = payload["jti"]
        token = OnetimeTokenRecords.objects.filter(jti=jti).first()
        if token:
            token.delete()
            return payload
        raise OneTimeTokenInvalidException


class JWTToken:
    """
    Class for generating and verifying jwt tokens used for authentication
    """

    signing_key = settings.JWT_SETTINGS["SIGNING_KEY"]
    verifying_key = settings.JWT_SETTINGS["VERIFYING_KEY"]
    algorithm = settings.JWT_SETTINGS["ALGORITHM"]
    issuer = settings.JWT_SETTINGS["ISSUER"]
    access_token_lifetime = settings.JWT_SETTINGS["ACCESS_TOKEN_LIFETIME"]
    refresh_token_lifetime = settings.JWT_SETTINGS["REFRESH_TOKEN_LIFETIME"]

    @classmethod
    def obtain(cls, payload: dict = None, type: AuthTokenType = None) -> str:
        """Generate a jwt token"""
        iat = timezone.now()
        token_lifetime: datetime.timedelta = (
            cls.access_token_lifetime
            if type == AuthTokenType.ACCESS_TOKEN
            else cls.refresh_token_lifetime
        )
        expires_at = iat + token_lifetime
        jti = uuid4().hex
        token = jwt.encode(
            payload={
                **payload,
                "iss": cls.issuer,
                "jti": jti,
                "exp": expires_at,
                "iat": iat,
                "type": type.value,
            },
            key=cls.signing_key,
            algorithm=cls.algorithm,
        )
        return token

    @classmethod
    def verify_token(
        cls, token: str = None, type: AuthTokenType = None
    ) -> Mapping[str, Any]:
        """Verify a token"""
        try:
            payload = jwt.decode(
                jwt=token, key=cls.verifying_key, algorithms=[cls.algorithm]
            )
            if payload["type"] != type.value:
                raise OneTimeTokenInvalidException
            return payload
        except jwt.ExpiredSignatureError:
            raise OneTimeTokenExpiredException
        except jwt.InvalidIssuerError:
            raise OneTimeTokenInvalidException

    @classmethod
    def obtain_refresh_token_for_user(cls, user: User = None) -> str:
        """Generate a refresh token for a user"""
        payload = {
            "user_id": str(user.id),
            "name": user.name,
            "email": user.email,
            "app": user.app.app_name,
        }
        return cls.obtain(payload=payload, type=AuthTokenType.REFRESH_TOKEN)

    @classmethod
    def obtain_access_token_by_refresh_token(cls, refresh_token: str = None) -> str:
        """Generate an access token by verifying a refresh token"""
        payload = cls.verify_token(
            token=refresh_token, type=AuthTokenType.REFRESH_TOKEN
        )
        return cls.obtain(payload=payload, type=AuthTokenType.ACCESS_TOKEN)
