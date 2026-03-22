from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Race


@method_decorator(csrf_exempt, name='dispatch')
class CarreraListView(View):
    def get(self, request):
        carreras = Race.objects.select_related('season', 'circuit').all()
        
        data = [
            {
                'id': c.id,
                'numero_ronda': c.round_number,
                'circuito': c.circuit.name if c.circuit else None,
                'fecha_carrera': c.race_date,
                'estado': c.status,
                'temporada': c.season.year if c.season else None,
            }
            for c in carreras
        ]
        
        # debug
        print("Carreras data:", data)
        
        return JsonResponse(data, safe=False)
