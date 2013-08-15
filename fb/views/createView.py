from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.facebook import Api
from fb.geo import Mapquest
from fb.models import Person, Location
from fb.storage import Store


class CreateView(View):

    person = None
    progress = 0
    api = None

    def get(self, request, id):

        # First check if a Person could be found for this id
        try:
            person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # Only start fetching data if an access_token has been set
        if person.access_token is not None:
            self.person = person
            self.api = Api(self.person.access_token)
            self.fetch_data()
        else:
            return HttpResponseNotFound

        # Make sure a response is returned
        return HttpResponse()

    def update_progress(self, level):
        self.person.progress = level
        self.person.save()

    def fetch_data(self):
        self.update_progress(0)
        self.fetch_friend_list()
        self.update_progress(25)
        self.fetch_user_data()
        self.update_progress(50)
        self.fetch_locations()
        self.update_progress(75)
        self.fetch_coordinates()
        self.update_progress(100)

    def fetch_friend_list(self):
        fb_friends = self.api.request(str(self.person.fb_id) + '/friends')
        for fb_friend in fb_friends:
            try:
                person = Person.objects.get(fb_id=fb_friend['id'])
            except Person.DoesNotExist:
                person = Person.objects.create(fb_id=fb_friend['id'])
            person.add_relationship(self.person)
            person.save()
        self.person.save()

    def fetch_user_data(self):
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id)
            })
        responses = self.api.mass_request(requests)
        for response in responses:
            store = Store()
            store.user(response, self.person)

    def fetch_locations(self):
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id) + '/locations'
            })
        responses = self.api.mass_request(requests)
        for response in responses:
            store = Store()
            store.location(response)

    def fetch_coordinates(self):

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
        self.store_coordinates(geo_data)

    def store_coordinates(self, geo_data):
        for geo_entry in geo_data:

            # Get all locations from the db that have the same name as the current location name
            try:
                locations = Location.objects.filter(name=geo_entry['providedLocation']['location'])
            except Location.DoesNotExist:
                continue

            # Check if Mapquest provided coordinates for this name
            try:
                coordinates = geo_entry['locations'][0]['latLng']
            except IndexError:
                continue

            # Set the coordinates and save the location
            for location in locations:
                location.latitude = coordinates['lat']
                location.longitude = coordinates['lng']
                location.save()