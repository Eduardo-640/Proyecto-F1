from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import auth_views

urlpatterns = [
    path("login/", auth_views.DriverLoginView.as_view(), name="auth-login"),
    path("register/", auth_views.DriverRegisterView.as_view(), name="auth-register"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", auth_views.DriverProfileView.as_view(), name="auth-me"),
]
