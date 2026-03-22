from django.http import JsonResponse
from django.views import View
from .models import Team


class EquipoListView(View):
    def get(self, request):
        equipos = Team.objects.all()
        
        data = [
            {
                'id': e.id,
                'nombre': e.name,
                'creditos': e.credits,
                'activo': e.active,
            }
            for e in equipos
        ]
        
        # debug
        print("Equipos data:", data)
        
        return JsonResponse(data, safe=False)
