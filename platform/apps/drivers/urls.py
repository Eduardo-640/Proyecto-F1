from django.urls import path
from . import views

urlpatterns = [
    # Endpoints públicos (sin autenticación)
    path(
        "public/drivers/",
        views.DriverListPublicView.as_view(),
        name="driver-list-public",
    ),
    path(
        "public/drivers/<int:pk>/",
        views.DriverDetailPublicView.as_view(),
        name="driver-detail-public",
    ),
    path("public/teams/", views.TeamListPublicView.as_view(), name="team-list-public"),
    path(
        "public/teams/<int:pk>/",
        views.TeamDetailPublicView.as_view(),
        name="team-detail-public",
    ),
    path("public/races/", views.RaceListPublicView.as_view(), name="race-list-public"),
    path(
        "public/races/<int:pk>/",
        views.RaceDetailPublicView.as_view(),
        name="race-detail-public",
    ),
    path(
        "public/seasons/",
        views.SeasonListPublicView.as_view(),
        name="season-list-public",
    ),
    path(
        "public/seasons/<int:pk>/",
        views.SeasonDetailPublicView.as_view(),
        name="season-detail-public",
    ),
    # Endpoints protegidos (requieren autenticación)
    path("drivers/", views.DriverListView.as_view(), name="driver-list"),
    path("drivers/<int:pk>/", views.DriverDetailView.as_view(), name="driver-detail"),
    path("teams/", views.TeamListView.as_view(), name="team-list"),
    path("teams/<int:pk>/", views.TeamDetailView.as_view(), name="team-detail"),
    path("races/", views.RaceListView.as_view(), name="race-list"),
    path("races/<int:pk>/", views.RaceDetailView.as_view(), name="race-detail"),
    path("seasons/", views.SeasonListView.as_view(), name="season-list"),
    path("seasons/<int:pk>/", views.SeasonDetailView.as_view(), name="season-detail"),
]
