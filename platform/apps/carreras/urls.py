from rest_framework.routers import DefaultRouter
from .views import CarreraViewSet, TransaccionCreditosViewSet

router = DefaultRouter()
router.register(r'carreras', CarreraViewSet, basename='carrera')
router.register(r'transacciones', TransaccionCreditosViewSet, basename='transaccion')

urlpatterns = router.urls
