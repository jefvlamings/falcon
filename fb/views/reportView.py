from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponseNotFound
from fb.models import Person
import datetime


class ReportView(View):

    person = None

    def get(self, request, id):

        # First check if a Person exists for this id
        try:
            self.person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # If the report is not yet ready, show a status of the report
        if self.person.progress < 100:
            return render(
                request,
                'status.html',
                {
                    'person': self.person,
                }
            )
        # Show the report
        else:
            return render(
                request,
                'report.html',
                {
                    'person': self.person,
                    'youngest_friends': self.person.friends.order_by('birthday').reverse()[:5],
                    'oldest_friends': self.person.friends.exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(birthday__isnull=False).order_by('birthday')[:5],
                    'nearest_hometowns': self.person.friends_hometowns[:5],
                    'furthest_hometowns': self.person.friends_hometowns[::-1][:5],
                    'furthest_travelers': self.person.furthest_travelers[::-1][:5],
                }
            )