from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken

from .services import AuthService
from .serializers import (
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
)
from drf_spectacular.utils import extend_schema


@extend_schema(tags=["Test"])
class TestApiView(APIView):

    def get(self, request):
        return Response({"message": "OK"})


@extend_schema(tags=["Client"])
class TokenObtainPairView(APIView):
    @extend_schema(responses={status.HTTP_200_OK: TokenObtainPairResponseSerializer})
    def post(self, request, *args, **kwargs):
        token_pair = AuthService.get_token_pair(request=request)
        print(token_pair)
        return Response(token_pair)


@extend_schema(tags=["Client"])
class TokenRefreshView(APIView):
    @extend_schema(responses={status.HTTP_200_OK: TokenRefreshResponseSerializer})
    def post(self, request, *args, **kwargs):
        access_token = AuthService.get_access_token(request=request)
        return Response(access_token)
