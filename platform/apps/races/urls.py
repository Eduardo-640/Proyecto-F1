from django.urls import path

from .views import (
    CarreraListView,
    DriverStatsView,
    RaceMetricsView,
    RaceTimelineView,
    TeamStatsView,
)

urlpatterns = [
    path('carreras/', CarreraListView.as_view(), name='carrera-list'),
    path('race/<int:pk>/metrics', RaceMetricsView.as_view(), name='race-metrics'),
    path('race/<int:pk>/timeline', RaceTimelineView.as_view(), name='race-timeline'),
    path('driver/<int:pk>/stats', DriverStatsView.as_view(), name='driver-stats'),
    path('team/<int:pk>/stats', TeamStatsView.as_view(), name='team-stats'),
]
