from django.views.generic.base import View
from django.http import HttpResponseNotFound, HttpResponse
from fb.models import Person, Location
import json


class TopTravelsView(View):

    person = None

    def get(self, request, id):

        # First check if a Person exists for this id
        try:
            self.person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # Create a JSON string from the results
        output = format_locations(self.top_travels())
        json_data = json.dumps(output)

        # Return the response
        return HttpResponse(json_data, mimetype="application/json")

    def top_travels(self):
        travels = Location.objects.filter(person_id=self.person.id).order_by('travel_distance')[::-1][:40]
        return travels


class TopTravelFriendsView(View):

    person = None

    def get(self, request, id):

        # First check if a Person exists for this id
        try:
            self.person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # Create a JSON string from the results
        output = format_locations(self.top_travel_friends())
        json_data = json.dumps(output)

        # Return the response
        return HttpResponse(json_data, mimetype="application/json")

    def top_travel_friends(self):
        from django.db import connection
        travels = Location.objects.raw(
            'SELECT * '
            'FROM `fb_location` AS a '
            'WHERE a.travel_distance = ('
                'SELECT MAX(travel_distance) '
                'FROM `fb_location` AS b '
                'WHERE b.person_id = a.person_id'
            ')'
            'ORDER BY a.travel_distance DESC '
        )[:30]

        print connection.queries
        return travels


class FurthestFriendsView(View):

    person = None

    def get(self, request, id):

        # First check if a Person exists for this id
        try:
            self.person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # Create a JSON string from the results
        output = format_locations(self.furthest_friends())
        json_data = json.dumps(output)

        # Return the response
        return HttpResponse(json_data, mimetype="application/json")

    def furthest_friends(self):
        hometowns = self.person.friends_hometowns.distinct().order_by('hometown_distance')[::-1][:10]
        return hometowns


def format_locations(locations):
    output = []
    for location in locations:
        try:
            person = Person.objects.get(id=location.person_id)
        except Person.DoesNotExist:
            continue
        output.append({
            'person': {
                'id': person.id,
                'fbid': person.fb_id,
                'name': person.name
            },
            'location': location.name,
            'latitude': location.latitude,
            'longitude': location.longitude,
        })
    return output