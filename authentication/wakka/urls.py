from django.urls import include, path

from config.constants import API_URL, VERIFY_URL

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
    path("user/<str:user_id>/", views.UserDetailView.as_view(), name="user-detail"),
]

verify_urlpatterns = [
    path(
        "verify-email/",
        views.EmailVerificationResponseView.as_view(),
        name="verify-email",
    ),
]

mail_urlpatterns = [
    path(
        "resend-verification-email/",
        views.EmailVerificationResendView.as_view(),
        name="resend-verification-email",
    ),
]

api_urlpatterns = [
    *token_urlpatterns,
    *test_urlpatterns,
    *user_urlpatterns,
    *mail_urlpatterns,
]


urlpatterns = [
    path(API_URL, include((api_urlpatterns, "wakka"), namespace="api")),
    path(VERIFY_URL, include((verify_urlpatterns, "wakka"), namespace="one-time")),
]
