from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.facebook import Api
from fb.geo import Mapquest
from fb.models import Person, Location
from fb.storage import Store
import fb.geo


class CreateView(View):

    person = None
    progress = 0
    number_of_requests = 0

    def get(self, request, id):

        # First check if a Person could be found for this id
        try:
            person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # Only start fetching data if an access_token has been set
        if person.access_token is not None:
            self.person = person
            self.fetch_data()
        else:
            return HttpResponseNotFound

        # Make sure a response is returned
        return HttpResponse()

    def fetch_data(self):
        self.update_progress(0)
        self.fetch_friend_list()
        self.update_progress(10)
        self.fetch_user_data()
        self.fetch_locations()
        self.fetch_geo_data()
        self.update_progress(90)
        self.store_distances()
        self.update_progress(100)

    def fetch_friend_list(self):
        request = {
            'id': self.person.fb_id,
            'request': str(self.person.fb_id) + '/friends'
        }
        number_of_requests = len(request)
        api = Api(self.person.access_token)
        generator = api.request([request])
        for responses in generator:
            for response in responses:
                for friend in response['data']:
                    try:
                        person = Person.objects.get(fb_id=friend['id'])
                    except Person.DoesNotExist:
                        person = Person.objects.create(fb_id=friend['id'])
                    person.add_relationship(self.person)
                    person.save()
            self.update_progress_by_api(number_of_requests, len(api.queued_requests), 10, 20)

    def fetch_user_data(self):
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id)
            })
        number_of_requests = len(requests)
        api = Api(self.person.access_token)
        generator = api.request(requests)
        for responses in generator:
            for response in responses:
                store = Store()
                store.user(response, self.person)
            self.update_progress_by_api(number_of_requests, len(api.queued_requests), 20, 40)

    def fetch_locations(self):
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id) + '/locations?limit=500'
            })
        number_of_requests = len(requests)
        api = Api(self.person.access_token)
        generator = api.request(requests)
        for responses in generator:
            for response in responses:
                try:
                    person = Person.objects.get(fb_id=response['id'])
                except Person.DoesNotExist:
                    continue
                for location in response['data']:
                    store = Store()
                    store.location(location, person)
            self.update_progress_by_api(number_of_requests, len(api.queued_requests), 40, 80)

    def fetch_geo_data(self):

        # Get all unique location names for which no latitude has been set
        locations = Location.objects.filter(latitude__isnull=True)
        location_names = []
        for location in locations:
            location_names.append(location.name)
        locations_names_unique = list(set(location_names))

        # Fetch all geocoding data for these location names
        mapquest = Mapquest()
        geo_data = mapquest.batch_request_names(locations_names_unique)

        # Process and store all geocoding data
        store = Store()
        store.geo_data(geo_data)

    def store_distances(self):
        self.store_distances_between_hometowns()
        self.store_distances_from_hometowns()

    def store_distances_between_hometowns(self):

        # Get all hometown locations for which no distance has been set
        locations = Location.objects.filter(hometown_distance__isnull=True, type='H')

        for location in locations:
            distance = fb.geo.distance(
                location.longitude,
                location.latitude,
                self.person.hometown.longitude,
                self.person.hometown.latitude
            )
            location.hometown_distance = distance
            location.save()

    def store_distances_from_hometowns(self):

        # Get all locations for which no distance has been set and which are not hometowns
        locations = Location.objects.filter(travel_distance__isnull=True, type='P')

        for location in locations:
            try:
                hometown = Location.objects.get(type='H', person_id=location.person_id)
            except Location.DoesNotExist:
                continue
            distance = fb.geo.distance(location.longitude, location.latitude, hometown.longitude, hometown.latitude)
            location.travel_distance = distance
            location.save()

    def update_progress(self, level):
        self.person.progress = level
        self.person.save()

    def update_progress_by_api(self, requests, queue, start, stop):
        progress_range = float(stop) - float(start)
        progress = float(start) + (((float(requests) - float(queue)) / float(requests)) * float(progress_range))
        self.person.progress = progress
        self.person.save()