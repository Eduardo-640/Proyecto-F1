from rest_framework.routers import DefaultRouter
from .views import DesarrolloEquipoViewSet

router = DefaultRouter()
router.register(r'desarrollo', DesarrolloEquipoViewSet, basename='desarrollo')

urlpatterns = router.urls
