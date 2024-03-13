from .models import Application
from .exceptions import InvalidAppNameException, InvalidServerApiKeyException
from config.env import ENV

# import request
from django.http.request import HttpRequest
from .urls import token_urlpatterns


class ServerAuthMiddleware(object):
    TOKEN_URL_NAMES = [url.name for url in token_urlpatterns]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        return self.get_response(request)

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        server_api_key = request.META.get("HTTP_X_SERVER_API_KEY")
        if request.resolver_match.url_name in self.TOKEN_URL_NAMES:
            return None

        if not server_api_key or not self.is_valid_server_api_key(server_api_key):
            raise InvalidServerApiKeyException

    def is_valid_server_api_key(self, server_api_key):
        return server_api_key == ENV.SERVER_API_KEY


class AppNameMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        return self.get_response(request)

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        URL_NAMES = [url.name for url in token_urlpatterns]
        app_name = request.META.get("HTTP_X_APP_NAME")
        if request.resolver_match.url_name not in URL_NAMES:
            return None
        if app_name:
            request.app_name = app_name
            if Application.objects.filter(app_name=app_name).exists():
                return None
        raise InvalidAppNameException
