from django.http import HttpRequest
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


from .constants import ACCESS_TOKEN_NAME, REFRESH_TOKEN_NAME

from .exceptions import InvalidCredentialsException, InvalidRefreshTokenException
from .models import User


class AuthService:

    @classmethod
    def get_user(cls, request: HttpRequest):
        data = request.data
        app_name = request.app_name
        email = data.get("username")
        password = data.get("password")
        user = User.objects.filter(email=email, app__app_name=app_name)
        if user.exists():
            user = user.first()
            if user.check_password(password):
                return user
        raise InvalidCredentialsException

    @classmethod
    def get_token_pair(cls, request: HttpRequest):
        user = cls.get_user(request)
        refresh = RefreshToken.for_user(user)
        refresh["email"] = user.email
        refresh["name"] = user.name
        refresh["app"] = user.app.app_name

        return {
            REFRESH_TOKEN_NAME: str(refresh),
            ACCESS_TOKEN_NAME: str(refresh.access_token),
        }

    @classmethod
    def get_access_token(cls, request: HttpRequest):
        refresh_token = request.data.get(REFRESH_TOKEN_NAME)
        if refresh_token:
            refresh_token = RefreshToken(refresh_token)
            refresh_token.verify()
            access_token = refresh_token.access_token
            return {ACCESS_TOKEN_NAME: str(access_token)}
        raise InvalidRefreshTokenException

    @classmethod
    def create_user(cls, email=None, password=None, **extra_fields):
        user = User.objects.create_user(email, password, **extra_fields)
        return user
