from rest_framework.routers import DefaultRouter
from .views import TemporadaViewSet

router = DefaultRouter()
router.register(r'temporadas', TemporadaViewSet, basename='temporada')

urlpatterns = router.urls
