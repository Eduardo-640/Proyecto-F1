from django.urls import path
from .views import EquipoListView

urlpatterns = [
    path('equipos/', EquipoListView.as_view(), name='equipo-list'),
]
