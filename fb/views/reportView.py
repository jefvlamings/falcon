from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponseNotFound
from fb.models import Person, Location
from django.db.models import Max
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
                    'youngest_friends': self.get_five_youngest_friends(),
                    'oldest_friends': self.get_five_oldest_friends(),
                    # 'nearest_hometowns': self.get_five_nearest_hometowns(),
                }
            )

    def get_five_youngest_friends(self):
        friends = self.person.friends.order_by('birthday').reverse()[:5]
        return friends

    def get_five_oldest_friends(self):
        friends = self.person.friends.exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(birthday__isnull=False).order_by('birthday')[:5]
        return friends

    def get_five_nearest_hometowns(self):
        hometowns = self.person.friends_hometowns.distinct().order_by('hometown_distance')[:5]
        furthest_hometowns = []
        for hometown in hometowns:
            try:
                person = Person.objects.get(id=hometown.person_id)
            except Person.DoesNotExist:
                continue
            furthest_hometowns.append({
                'person': person,
                'location': hometown
            })
        return furthest_hometowns