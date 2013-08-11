from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.models import Person
import json


class ProgressView(View):

    def get(self, request, id):
        try:
            person = Person.objects.get(pk=id)
            import decimal
            progress = round(decimal.Decimal(person.progress), 2)
            json_data = json.dumps(progress);
            return HttpResponse(json_data, mimetype="application/json")
        except Person.DoesNotExist:
            return HttpResponseNotFound()