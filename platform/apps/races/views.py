from django.http import JsonResponse
from django.views import View
from .models import Race


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
