from django.urls import path
from .views import EntryListView, SetupsCarreraView

urlpatterns = [
    path('setups/carrera/<int:carrera_id>/entry_list/', EntryListView.as_view(), name='entry-list'),
    path('setups/carrera/<int:carrera_id>/setups/', SetupsCarreraView.as_view(), name='setups-carrera'),
]
