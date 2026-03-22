from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Team


@method_decorator(csrf_exempt, name='dispatch')
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
