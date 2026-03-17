from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .services import entry_list_para_carrera, setups_para_carrera


class EntryListView(APIView):
    """GET /api/setups/carrera/{carrera_id}/entry_list/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, carrera_id):
        try:
            contenido = entry_list_para_carrera(carrera_id)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)

        response = HttpResponse(contenido, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="entry_list.ini"'
        return response


class SetupsCarreraView(APIView):
    """GET /api/setups/carrera/{carrera_id}/setups/"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, carrera_id):
        try:
            setups = setups_para_carrera(carrera_id)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=400)

        # Devolver como JSON { nombre_archivo: contenido }
        return Response(setups)
