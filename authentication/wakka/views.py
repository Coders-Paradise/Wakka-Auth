from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from wakka.authentication import WakkaAppNameAuthentication, WakkaServerAuthentication

from . import serializers
from .services import AuthService


@extend_schema(tags=["Test"])
class TestApiView(APIView):
    authentication_classes = [WakkaServerAuthentication]

    def get(self, request):
        return Response({"message": "OK"})


@extend_schema(tags=["Client"])
class TokenObtainPairView(APIView):
    authentication_classes = [WakkaAppNameAuthentication]

    @extend_schema(
        request=serializers.TokenPairRequestSeralizer,
        responses={status.HTTP_200_OK: serializers.TokenPairResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        token_pair = AuthService.get_token_pair(request=request)
        serializer = serializers.TokenPairResponseSerializer(token_pair)
        return Response(serializer.data)


@extend_schema(tags=["Client"])
class TokenRefreshView(APIView):
    authentication_classes = [WakkaAppNameAuthentication]

    @extend_schema(
        request=serializers.TokenRefreshRequestSerializer,
        responses={status.HTTP_200_OK: serializers.TokenRefreshResponseSerializer},
    )
    def post(self, request, *args, **kwargs):
        access_token = AuthService.get_access_token(request=request)
        serializer = serializers.TokenRefreshResponseSerializer(access_token)
        return Response(serializer.data)
