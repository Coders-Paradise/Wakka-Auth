from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)

from .constants import ADMIN_URL, API_URL, DOCS_URL
from .env import ENV

spectacular_urls = [
    path(DOCS_URL + "schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        DOCS_URL + "swagger/",
        SpectacularSwaggerView.as_view(),
        name="swagger",
    ),
    path(
        DOCS_URL + "redoc/",
        SpectacularRedocView.as_view(),
        name="redoc",
    ),
]

admin_urls = [
    path(ADMIN_URL, admin.site.urls, name="admin"),
]

urlpatterns = [
    *admin_urls,
    path(API_URL, include("wakka.urls"), name="api"),
]


if ENV.DEBUG == "True":
    urlpatterns += spectacular_urls
