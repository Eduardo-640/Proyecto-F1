from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth JWT
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Apps
    path('api/', include('apps.equipos.urls')),
    path('api/', include('apps.pilotos.urls')),
    path('api/', include('apps.temporadas.urls')),
    path('api/', include('apps.carreras.urls')),
    path('api/', include('apps.desarrollo.urls')),
    path('api/', include('apps.setups.urls')),
]
