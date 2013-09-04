from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.models import Progress
import json
import decimal


class ProgressView(View):

    def get(self, request, id):
        try:
            progress = Progress.objects.get(pk=id)
        except Progress.DoesNotExist:
            return HttpResponseNotFound()

        progress = {
            'percentage': round(decimal.Decimal(progress.percentage), 2),
            'description': progress.description
        }
        json_data = json.dumps(progress)
        return HttpResponse(json_data, content_type="application/json")