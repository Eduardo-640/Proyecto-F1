from django.urls import path
from .views import CarreraListView

urlpatterns = [
    path('carreras/', CarreraListView.as_view(), name='carrera-list'),
]
