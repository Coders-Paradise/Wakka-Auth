from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from . import serializers
from .authentication import WakkaAppNameAuthentication, WakkaServerAuthentication
from .constants import (
    FORGOT_PASSWORD_EXPIRED_LINK_DESCRIPTION,
    FORGOT_PASSWORD_EXPIRED_LINK_TITLE,
    FORGOT_PASSWORD_FORM_TITLE,
    FORGOT_PASSWORD_INVALID_LINK_DESCRIPTION,
    FORGOT_PASSWORD_INVALID_LINK_TITLE,
    FORGOT_PASSWORD_SUCCESS_DESCRIPTION,
    FORGOT_PASSWORD_SUCCESS_TITLE,
    VERIFICATION_EXPIRED_LINK_DESCRIPTION,
    VERIFICATION_EXPIRED_LINK_TITLE,
    VERIFICATION_INVALID_LINK_DESCRIPTION,
    VERIFICATION_INVALID_LINK_TITLE,
    VERIFICATION_SUCCESS_DESCRIPTION,
    VERIFICATION_SUCCESS_TITLE,
    OneTimeTokenType,
)
from .exceptions import OneTimeTokenExpiredException, OneTimeTokenInvalidException
from .services import AuthService
from .utils import WakkaResponse


class HealthCheckView(APIView):
    def get(self, request: Request):
        status = AuthService.health_check()
        serializer = serializers.HealthCheckResponseSerializer(status)
        return WakkaResponse(serializer.data)


@extend_schema(tags=["Test"])
class TestApiView(APIView):
    authentication_classes = [WakkaAppNameAuthentication, WakkaServerAuthentication]

    def get(self, request: Request):
        return WakkaResponse({"message": "OK"})


@extend_schema(tags=["Client"])
class TokenObtainPairView(APIView):
    authentication_classes = [WakkaAppNameAuthentication]

    @extend_schema(
        request=serializers.TokenPairRequestSeralizer,
        responses={status.HTTP_200_OK: serializers.TokenPairResponseSerializer},
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = serializers.TokenPairRequestSeralizer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_pair = AuthService.get_token_pair(
            **serializer.validated_data, app=request.app
        )
        serializer = serializers.TokenPairResponseSerializer(token_pair)
        return WakkaResponse(serializer.data)


@extend_schema(tags=["Client"])
class TokenRefreshView(APIView):
    authentication_classes = [WakkaAppNameAuthentication]

    @extend_schema(
        request=serializers.TokenRefreshRequestSerializer,
        responses={status.HTTP_200_OK: serializers.TokenRefreshResponseSerializer},
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = serializers.TokenRefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = AuthService.get_access_token(**serializer.validated_data)
        serializer = serializers.TokenRefreshResponseSerializer(access_token)
        return WakkaResponse(serializer.data)


@extend_schema(tags=["Server"])
class UserView(APIView):
    authentication_classes = [WakkaAppNameAuthentication, WakkaServerAuthentication]

    @extend_schema(
        request=serializers.UserCreateRequestSerializer,
        responses={status.HTTP_201_CREATED: serializers.UserResponseSerializer},
        description="Create a new user",
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = serializers.UserCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AuthService.create_user(**serializer.validated_data, app=request.app)
        serializer = serializers.UserResponseSerializer(user)
        return WakkaResponse(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Server"])
class UserDetailView(APIView):
    authentication_classes = [WakkaAppNameAuthentication, WakkaServerAuthentication]

    @extend_schema(
        responses={status.HTTP_200_OK: serializers.UserResponseSerializer},
        description="Get user details",
    )
    def get(self, request: Request, user_id: str, *args, **kwargs):
        user = AuthService.get_user_by_id(user_id)
        AuthService.send_verification_email(
            user=user,
            app=request.app,
            domain=request.get_host(),
            protocol=request.scheme,
        )
        serializer = serializers.UserResponseSerializer(user)
        return WakkaResponse(serializer.data)

    @extend_schema(
        request=serializers.UserUpdateRequestSerializer,
        responses={status.HTTP_200_OK: serializers.UserResponseSerializer},
        description="Update user details",
    )
    def put(self, request: Request, user_id: str, *args, **kwargs):
        serializer = serializers.UserUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AuthService.update_user(user_id, **serializer.validated_data)
        serializer = serializers.UserResponseSerializer(user)
        return WakkaResponse(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: None}, description="Delete user"
    )
    def delete(self, request: Request, user_id: str, *args, **kwargs):
        AuthService.delete_user(user_id)
        return WakkaResponse(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Email Verification"])
class EmailVerificationPageView(APIView):

    @extend_schema(
        description="Email verification page",
    )
    def get(self, request: Request, *args, **kwargs):
        try:
            token = request.GET.get("token")
            AuthService.validate_email_verification_token(token=token)
        except OneTimeTokenExpiredException:
            return render(
                request,
                "email_verification_page.html",
                {
                    "title": VERIFICATION_EXPIRED_LINK_TITLE,
                    "description": VERIFICATION_EXPIRED_LINK_DESCRIPTION,
                },
                status=400,
            )
        except OneTimeTokenInvalidException:
            return render(
                request,
                "email_verification_page.html",
                {
                    "title": VERIFICATION_INVALID_LINK_TITLE,
                    "description": VERIFICATION_INVALID_LINK_DESCRIPTION,
                },
                status=400,
            )
        return render(
            request,
            "email_verification_page.html",
            {
                "title": VERIFICATION_SUCCESS_TITLE,
                "description": VERIFICATION_SUCCESS_DESCRIPTION,
            },
            status=200,
        )


@extend_schema(tags=["Email Verification"])
class EmailVerificationSendView(APIView):
    authentication_classes = [WakkaAppNameAuthentication]

    @extend_schema(
        request=serializers.EmailVerificationRequestSerializer,
        responses={status.HTTP_200_OK: None},
        description="Send email verification link",
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = serializers.EmailVerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AuthService.get_user_by_id(serializer.validated_data["user_id"])

        AuthService.send_verification_email(
            user=user,
            app=user.app,
            domain=request.get_host(),
            protocol=request.scheme,
        )

        return WakkaResponse(status=status.HTTP_200_OK)


@extend_schema(tags=["Forgot Password"])
class ForgotPasswordSendView(APIView):
    authentication_classes = [WakkaAppNameAuthentication]

    @extend_schema(
        request=serializers.ForgotPasswordRequestSerializer,
        responses={status.HTTP_200_OK: None},
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = serializers.ForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = AuthService.get_user_by_email(
            email=serializer.validated_data["email"],
            app=request.app,
        )
        if user:
            AuthService.send_FORGOT_password_email(
                user=user,
                app=user.app,
                domain=request.get_host(),
                protocol=request.scheme,
            )

        return WakkaResponse(status=status.HTTP_200_OK)


@extend_schema(tags=["Forgot Password"])
class ForgotPasswordPageView(APIView):

    @extend_schema(
        description="Forgot Password page",
    )
    def get(self, request: Request, *args, **kwargs):
        try:
            token = request.GET.get("token")
            payload = AuthService.validate_forgot_password_token(token=token)
            # get the user in the payload and generate a new token for the form
            # which will be used to reset the password
            user = AuthService.get_user_by_id(payload.get("user_id"))
            reset_password_form_token = (
                AuthService.generate_one_time_verification_token(
                    user=user, type=OneTimeTokenType.FOROGT_PASSWORD.value
                )
            )
            return render(
                request,
                "forgot_password_page.html",
                {
                    "title": FORGOT_PASSWORD_FORM_TITLE,
                    "description": None,
                    "type": "FORM",
                    "token": reset_password_form_token,
                },
                status=200,
            )
        except OneTimeTokenExpiredException:
            return render(
                request,
                "forgot_password_page.html",
                {
                    "title": FORGOT_PASSWORD_EXPIRED_LINK_TITLE,
                    "description": FORGOT_PASSWORD_EXPIRED_LINK_DESCRIPTION,
                    "type": "ERROR",
                },
                status=400,
            )
        except OneTimeTokenInvalidException:
            return render(
                request,
                "forgot_password_page.html",
                {
                    "title": FORGOT_PASSWORD_INVALID_LINK_TITLE,
                    "description": FORGOT_PASSWORD_INVALID_LINK_DESCRIPTION,
                    "type": "ERROR",
                },
                status=400,
            )
        except Exception as e:
            raise e

    @extend_schema(
        request=serializers.ForgotPasswordFormSerializer,
        responses={status.HTTP_200_OK: None},
        description="Used by forgot password page to reset password.",
    )
    def post(self, request: Request, *args, **kwargs):
        serializer = serializers.ForgotPasswordFormSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = serializer.validated_data["token"]
            password = serializer.validated_data["new_password"]
            # Validate the token and get the user, then change the password
            payload = AuthService.validate_forgot_password_token(token=token)
            user = AuthService.get_user_by_id(user_id=payload.get("user_id"))
            AuthService.change_password(
                user=user,
                password=password,
            )
            return render(
                request,
                "forgot_password_page.html",
                {
                    "title": FORGOT_PASSWORD_SUCCESS_TITLE,
                    "description": FORGOT_PASSWORD_SUCCESS_DESCRIPTION,
                    "type": "SUCCESS",
                },
                status=200,
            )
        except OneTimeTokenExpiredException:
            return render(
                request,
                "forgot_password_page.html",
                {
                    "title": FORGOT_PASSWORD_EXPIRED_LINK_TITLE,
                    "description": FORGOT_PASSWORD_EXPIRED_LINK_DESCRIPTION,
                    "type": "ERROR",
                },
                status=400,
            )
        except OneTimeTokenInvalidException:
            return render(
                request,
                "forgot_password_page.html",
                {
                    "title": FORGOT_PASSWORD_INVALID_LINK_TITLE,
                    "description": FORGOT_PASSWORD_INVALID_LINK_DESCRIPTION,
                    "type": "ERROR",
                },
                status=400,
            )
        except Exception as e:
            raise e
