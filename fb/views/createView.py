from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.facebook import Api
from fb.geo import Mapquest
from fb.models import Person, Location, Progress
from fb.storage import Store
import fb.geo


class CreateView(View):

    person = None
    progress = None
    number_of_requests = 0

    def get(self, request, id):

        # First check if a Person could be found for this id
        try:
            self.person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # Check if a progress exists for this Person, otherwise create one
        try:
            self.progress = Progress.objects.get(person=self.person)
        except Progress.DoesNotExist:
            self.progress = Progress.objects.create(
                person=self.person,
                percentage=0,
                description='Let\'s create a report for you!'
            )

        # Only start fetching data if an access_token has been set
        if self.person.access_token is not None:
            self.fetch_data()
        else:
            return HttpResponseNotFound

        # Make sure a response is returned
        return HttpResponse()

    def fetch_data(self):

        # TODO: Fetch user hometowns by its location ID
        # TODO: Document each function

        self.fetch_friend_list()
        self.fetch_user_data()
        self.fetch_locations()
        # self.fetch_geo_data()
        self.store_distances()

    def fetch_friend_list(self):

        self.update_progress(1, 'Collect a list of all your friends')

        request = {
            'id': self.person.fb_id,
            'request': str(self.person.fb_id) + '/friends'
        }
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

    def fetch_user_data(self):

        self.update_progress(10, 'Collecting general information of each of your friends.')

        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id)
            })
        api = Api(self.person.access_token)
        requested = len(requests)
        generator = api.request(requests)
        for responses in generator:
            for response in responses:
                store = Store()
                store.user(response, self.person)
            processed_total = requested - len(api.queued_requests)
            self.update_progress(
                self.calculate_progress_by_queue(requested, len(api.queued_requests), 20, 40),
                'General information for %s of %s friends already fetched' % (processed_total, requested)
            )

    def fetch_locations(self):

        self.update_progress(40, 'Collecting your and your friends locations.')

        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id) + '/locations?limit=500'
            })
        api = Api(self.person.access_token)
        requested = len(requests)
        generator = api.request(requests)
        location_count = 0
        for responses in generator:
            for response in responses:
                try:
                    person = Person.objects.get(fb_id=response['id'])
                except Person.DoesNotExist:
                    continue
                for location in response['data']:
                    location_count += 1
                    store = Store()
                    store.location(location, person)

            self.update_progress(
                self.calculate_progress_by_queue(requested, len(api.queued_requests), 40, 80),
                '%s locations collected sofar' % location_count
            )

    def fetch_geo_data(self):

        # Get all unique location names for which no latitude has been set
        locations = Location.objects.filter(country__isnull=True)
        location_names = []
        for location in locations:
            location_names.append(location.name)
        locations_names_unique = list(set(location_names))

        # Fetch all geocoding data for these location names
        mapquest = Mapquest()
        generator = mapquest.batch_request_names(locations_names_unique)
        for responses in generator:
            for response in responses:
                # Process and store geocoding data
                store = Store()
                store.geo_data(response)


    def store_distances(self):
        self.update_progress(80, 'Calculating distances between your hometown and those of your friends.')
        self.store_distances_between_hometowns()
        self.update_progress(90, 'Calculating travel distances for you and each of your friends.')
        self.store_distances_from_hometowns()
        self.update_progress(100, 'Creating a report based on all collected information.')

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

    def update_progress(self, percentage, description):
        self.progress.percentage = percentage
        self.progress.description = description
        self.progress.save()

    def calculate_progress_by_queue(self, total, togo, begin, end):
        progress_range = float(end) - float(begin)
        percentage = float(begin) + (((float(total) - float(togo)) / float(total)) * float(progress_range))
        return percentage