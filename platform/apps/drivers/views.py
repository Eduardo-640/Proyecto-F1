from django.http import JsonResponse
from django.views import View
from .models import Driver


class PilotoListView(View):
    def get(self, request):
        pilotos = Driver.objects.select_related('team').all()
        
        data = [
            {
                'id': p.id,
                'nombre': p.name,
                'apellido': p.last_name,
                'numero': p.number,
                'pais': p.country,
                'fecha_nacimiento': p.birth_date,
                'equipo__nombre': p.team.name if p.team else None,
            }
            for p in pilotos
        ]
        
        #debug
        print("Pilotos data:", data)
        
        return JsonResponse({'pilotos': data})
