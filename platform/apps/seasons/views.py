from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .models import Season


@method_decorator(csrf_exempt, name='dispatch')
class TemporadaListView(View):
    def get(self, request):
        temporadas = Season.objects.all()
        
        data = [
            {
                'id': t.id,
                'nombre': t.name,
                'año': t.year,
                'edicion': t.edition,
                'activa': t.active,
                'fecha_inicio': t.start_date,
                'fecha_fin': t.end_date,
            }
            for t in temporadas
        ]
        
        # debug
        print("Temporadas data:", data)
        
        return JsonResponse(data, safe=False)
