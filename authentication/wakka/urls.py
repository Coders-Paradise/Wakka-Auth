from django.urls import path

from . import views

test_urlpatterns = [path("test/", views.TestApiView.as_view(), name="test")]
token_urlpatterns = [
    path(
        "obtain-token/",
        views.TokenObtainPairView.as_view(),
        name="obtain_token",
    ),
    path("refresh-token/", views.TokenRefreshView.as_view(), name="refresh_token"),
]

user_urlpatterns = [
    path("user/", views.UserView.as_view(), name="user"),
]

urlpatterns = [*token_urlpatterns, *test_urlpatterns, *user_urlpatterns]
