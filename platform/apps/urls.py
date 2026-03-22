from django.urls import path, include

app_name = "apps"

urlpatterns = [
    path("", include("apps.drivers.urls")),
    path("", include("apps.races.urls")),
    path("", include("apps.teams.urls")),
    path("", include("apps.seasons.urls")),
    # path("seasons/", include("apps.seasons.urls", namespace="seasons")),
]
