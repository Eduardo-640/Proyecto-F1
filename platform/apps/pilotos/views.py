from rest_framework import viewsets, permissions
from .models import Piloto
from .serializers import PilotoSerializer


class PilotoViewSet(viewsets.ModelViewSet):
    queryset = Piloto.objects.select_related('equipo').all()
    serializer_class = PilotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
