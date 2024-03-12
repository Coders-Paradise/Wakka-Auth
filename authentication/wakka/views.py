from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
)
from drf_spectacular.utils import extend_schema


class TestApiView(APIView):

    def get(self, request):
        return Response({"message": "OK"})


@extend_schema(tags=["Client"])
class TokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        responses={
            status.HTTP_200_OK: TokenObtainPairResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, args, kwargs)


@extend_schema(tags=["Client"])
class TokenRefreshView(TokenRefreshView):
    @extend_schema(
        responses={
            status.HTTP_200_OK: TokenRefreshResponseSerializer,
        }
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, args, kwargs)
