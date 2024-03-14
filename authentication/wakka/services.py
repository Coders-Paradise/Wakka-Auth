from django.http import HttpRequest
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .constants import ACCESS_TOKEN_NAME, REFRESH_TOKEN_NAME
from .exceptions import (InvalidAppNameException, InvalidCredentialsException,
                         InvalidRefreshTokenException,
                         UserAlreadyExistsException)
from .models import Application, User
from .serializers import (TokenPairRequestSeralizer,
                          TokenRefreshRequestSerializer)


class AuthService:

    @classmethod
    def get_user(cls, request: HttpRequest):
        data = request.data
        serializer = TokenPairRequestSeralizer(data=data)
        if serializer.is_valid(raise_exception=True):
            app_name = request.app_name
            email = serializer.validated_data.get("email")
            password = serializer.validated_data.get("password")
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
        serializer = TokenRefreshRequestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            refresh_token = serializer.validated_data.get(REFRESH_TOKEN_NAME)
        if refresh_token:
            refresh_token = RefreshToken(refresh_token)
            refresh_token.verify()
            access_token = refresh_token.access_token
            return {ACCESS_TOKEN_NAME: str(access_token)}
        raise InvalidRefreshTokenException

    @classmethod
    def create_user(
        cls,
        email: str = None,
        password: str = None,
        name: str = None,
        app: Application = None,
        **extra_fields,
    ):
        user = User.objects.include_deleted().filter(email=email, app=app)
        """
        Checks if user already exists.
        Case 1: User exists but soft deleted -> Hard delete the user and create a new user
        Case 2: User exists but not soft deleted -> Raise UserAlreadyExistsException
        """
        if user.exists():
            user = user.first()
            if user.deleted_at: # Case 1
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
