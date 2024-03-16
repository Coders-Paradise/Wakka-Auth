from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from . import serializers
from .authentication import WakkaAppNameAuthentication, WakkaServerAuthentication
from .constants import (
    VERIFICATION_EXPIRED_LINK_DESCRIPTION,
    VERIFICATION_EXPIRED_LINK_TITLE,
    VERIFICATION_INVALID_LINK_DESCRIPTION,
    VERIFICATION_INVALID_LINK_TITLE,
    VERIFICATION_SUCCESS_DESCRIPTION,
    VERIFICATION_SUCCESS_TITLE,
)
from .exceptions import OneTimeTokenExpiredException, OneTimeTokenInvalidException
from .services import AuthService


@extend_schema(tags=["Test"])
class TestApiView(APIView):
    authentication_classes = [WakkaServerAuthentication]

    def get(self, request: Request):
        return Response({"message": "OK"})


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
        return Response(serializer.data)


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
        return Response(serializer.data)


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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        return Response(serializer.data)

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
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={status.HTTP_204_NO_CONTENT: None}, description="Delete user"
    )
    def delete(self, request: Request, user_id: str, *args, **kwargs):
        AuthService.delete_user(user_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Email Verification"])
class EmailVerificationResponseView(APIView):

    def get(self, request: Request, *args, **kwargs):
        try:
            token = request.GET.get("token")
            AuthService.perform_email_verification(token=token)
        except OneTimeTokenExpiredException:
            return render(
                request,
                "email_verification_response.html",
                {
                    "title": VERIFICATION_EXPIRED_LINK_TITLE,
                    "description": VERIFICATION_EXPIRED_LINK_DESCRIPTION,
                },
                status=400,
            )
        except OneTimeTokenInvalidException:
            return render(
                request,
                "email_verification_response.html",
                {
                    "title": VERIFICATION_INVALID_LINK_TITLE,
                    "description": VERIFICATION_INVALID_LINK_DESCRIPTION,
                },
                status=400,
            )
        return render(
            request,
            "email_verification_response.html",
            {
                "title": VERIFICATION_SUCCESS_TITLE,
                "description": VERIFICATION_SUCCESS_DESCRIPTION,
            },
            status=200,
        )


@extend_schema(tags=["Email Verification"])
class EmailVerificationResendView(APIView):
    @extend_schema(request=serializers.EmailVerificationRequestSerializer)
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

        return Response(status=status.HTTP_200_OK)
