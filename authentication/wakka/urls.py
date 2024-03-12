from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

token_urlpatterns = [
    path(
        "obtain-token/",
        views.TokenObtainPairView.as_view(),
        name="obtain_token",
    ),
    path("refresh-token/", views.TokenRefreshView.as_view(), name="refresh_token"),
]

test_urlpatterns = [path("test/", views.TestApiView.as_view(), name="test")]

urlpatterns = [*token_urlpatterns, *test_urlpatterns]
