from rest_framework.routers import DefaultRouter
from .views import PilotoViewSet

router = DefaultRouter()
router.register(r'pilotos', PilotoViewSet, basename='piloto')

urlpatterns = router.urls
