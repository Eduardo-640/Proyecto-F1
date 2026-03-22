from django.urls import path
from .views import TemporadaListView

urlpatterns = [
    path('temporadas/', TemporadaListView.as_view(), name='temporada-list'),
]
