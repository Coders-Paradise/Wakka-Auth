import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import Token

from .models import User


class HealthCheckResponseSerializer(serializers.Serializer):
    database = serializers.BooleanField()
    server = serializers.BooleanField()


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


class UserCreateRequestSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    password = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = User
        fields = ["email", "password", "name"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def validate(self, attrs):
        email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if re.match(r"[a-zA-Z_ ]+", attrs["name"]) == None:
            raise serializers.ValidationError("Invalid name format")

        if re.match(email_regex, attrs["email"]) is None:
            raise serializers.ValidationError("Invalid email format")

        try:
            validate_password(attrs["password"])
        except Exception as e:
            raise serializers.ValidationError(e)
        return super().validate(attrs)


class UserUpdateRequestSerializer(serializers.ModelSerializer):
    # email = serializers.CharField() # Currently not allowing email update
    name = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)

    class Meta:
        model = User
        # fields = ["email", "name", "is_active"]
        fields = ["name", "is_active"]

    def create(self, validated_data):
        raise NotImplementedError()

    def validate(self, attrs):
        email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if re.match(r"[a-zA-Z_ ]+", attrs["name"]) == None:
            raise serializers.ValidationError("Invalid name format")
        # if re.match(email_regex, attrs["email"]) is None:
        #     raise serializers.ValidationError("Invalid email format")

        return super().validate(attrs)


class UserResponseSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    email = serializers.CharField()
    name = serializers.CharField()
    app = serializers.CharField(source="app.app_name")
    date_joined = serializers.DateTimeField()
    is_active = serializers.BooleanField()
    verified = serializers.BooleanField()

    class Meta:
        model = User
        fields = ["id", "email", "name", "app", "date_joined", "is_active", "verified"]


class EmailVerificationRequestSerializer(serializers.Serializer):
    user_id = serializers.CharField()


class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.CharField()


class ForgotPasswordFormSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    token = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        try:
            validate_password(attrs["new_password"])
        except Exception as e:
            raise serializers.ValidationError(e)
        return super().validate(attrs)
