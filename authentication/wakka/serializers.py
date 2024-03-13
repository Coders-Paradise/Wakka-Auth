import re
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import Token
from .models import User
from rest_framework import serializers


class TokenPairRequestSeralizer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def validate(self, attrs):
        if re.match(r"[^@]+@[^@]+\.[^@]+", attrs["email"]) == None:
            raise serializers.ValidationError("Invalid email format")
        return super().validate(attrs)


class TokenPairResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class TokenRefreshRequestSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class TokenRefreshResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()
