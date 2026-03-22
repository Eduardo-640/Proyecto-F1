from django.urls import path
from .views import PilotoListView

urlpatterns = [
    path('pilotos/', PilotoListView.as_view(), name='piloto-list'),
]
