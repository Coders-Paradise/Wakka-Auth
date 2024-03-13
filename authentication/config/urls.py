from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from .env import ENV

spectacular_urls = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(),
        name="swagger",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(),
        name="redoc",
    ),
]

urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("api/v1/", include("wakka.urls"), name="api"),
]


if ENV.DEBUG == "True":
    urlpatterns += spectacular_urls
