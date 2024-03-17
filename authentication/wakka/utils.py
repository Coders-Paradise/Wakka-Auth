import datetime
from typing import Any, Mapping
from uuid import uuid4

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework.response import Response

from .exceptions import OneTimeTokenExpiredException, OneTimeTokenInvalidException
from .models import OnetimeTokenRecords


class WakkaResponse(Response):

    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
    ):
        """
        Restructuring the data to be returned in the response
        Schema: {
            "data": data,
            "status": status
        }"""
        if status:
            actual_data = data
            data = {"data": actual_data, "status": status}
        super().__init__(data, status, template_name, headers, exception, content_type)


class OneTimeJWTToken:
    """Generating and verifying one time jwt tokens for email verification and password reset"""

    signing_key = settings.SIMPLE_JWT["SIGNING_KEY"]
    verifying_key = settings.SIMPLE_JWT["VERIFYING_KEY"]
    algorithm = settings.SIMPLE_JWT["ALGORITHM"]
    issuer = settings.SIMPLE_JWT["ISSUER"]

    @classmethod
    def obtain(cls, payload: dict, lifetime: int) -> str:
        """Generate a one time jwt token"""
        jti = uuid4().hex
        expires_at = timezone.now() + datetime.timedelta(minutes=lifetime)
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
