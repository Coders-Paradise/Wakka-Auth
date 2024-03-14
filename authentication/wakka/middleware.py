from config.constants import ADMIN_URL, DOCS_URL
from config.env import ENV
from django.contrib.auth.hashers import check_password
from django.http.request import HttpRequest

from .exceptions import InvalidAppNameException, InvalidServerApiKeyException
from .models import Application
from .urls import test_urlpatterns, token_urlpatterns

# url paths to exclude from the middleware
WHITELIST_URLS = [
    DOCS_URL,
    ADMIN_URL,
]


class AppNameMiddleware(object):
    """Validates the app name for all requests"""

    EXCLUDE_URL_NAMES = [url.name for url in token_urlpatterns]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        return self.get_response(request)

    def process_view(self, request: HttpRequest, view_func, view_args, view_kwargs):
        app_name = request.META.get("HTTP_X_APP_NAME")
        is_whitelisted_url = any(
            request.path.startswith(f"/{url}") for url in WHITELIST_URLS
        )
        is_excluded_url = request.resolver_match.url_name in self.EXCLUDE_URL_NAMES
        print(WHITELIST_URLS, request.path)
        if is_whitelisted_url or is_excluded_url:
            return None
        if app_name:
            app = Application.objects.filter(app_name=app_name).first()
            if app:
                request.app_name = app_name
                request.app = app
                return None

        raise InvalidAppNameException
