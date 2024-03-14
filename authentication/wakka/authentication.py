from django.contrib.auth.hashers import check_password
from django.http import HttpRequest
from rest_framework.authentication import BaseAuthentication

from .exceptions import InvalidAppNameException, InvalidServerApiKeyException
from .models import Application


class WakkaAppNameAuthentication(BaseAuthentication):
    def authenticate(self, request: HttpRequest):
        app_name = request.META.get("HTTP_X_APP_NAME")
        app = Application.objects.filter(app_name=app_name).first()
        if app:
            request.app_name = app_name
            request.app = app
            return None
        raise InvalidAppNameException

class WakkaServerAuthentication(BaseAuthentication):

    def authenticate(self, request: HttpRequest):
        if not hasattr(request, "app_name"):
            raise InvalidAppNameException
        app: Application = request.app
        server_api_key = request.META.get("HTTP_X_SERVER_API_KEY")
        server_api_key_hash = app.server_api_key_hash
        if check_password(server_api_key, server_api_key_hash):
            return None
        raise InvalidServerApiKeyException
