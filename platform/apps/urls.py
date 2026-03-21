from django.urls import path, include

app_name = "apps"

urlpatterns = [
    path("", include("apps.drivers.urls")),
    # path("seasons/", include("apps.seasons.urls", namespace="seasons")),
]
