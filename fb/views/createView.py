from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.facebook import Api
from fb.geo import Mapquest
from fb.models import Person, Location, Progress
from fb.storage import Store
import fb.geo


class CreateView(View):
    """
    Class that fetches data from the Facebook API an monitors this process
    by keeping track of its progress
    """

    person = None
    progress = None
    number_of_requests = 0

    def get(self, request, id):
        """
        Get function checks if a person exists for a given id.
        Afterwards data fetching, using the Facebook API, will be initiated
        """
        try:
            self.person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()
        if self.person.access_token is not None:
            # Only start fetching data if an access_token has been set
            self.fetch_data()
        else:
            return HttpResponseNotFound
        return HttpResponse()

    def fetch_data(self):
        self.start_progress()
        self.fetch_friend_list()
        self.fetch_user_data()
        self.fetch_locations()
        self.fetch_locations_by_fb_id()
        self.store_distances()

    def start_progress(self):
        """
        We continously monitor the data fetching progress. This function makes
        sure a Progress object is available to keep track of all processes
        """
        try:
            self.progress = Progress.objects.get(person=self.person)
        except Progress.DoesNotExist:
            self.progress = Progress.objects.create(
                person=self.person,
                percentage=0,
                description='Let\'s create a report for you!'
            )

    def fetch_friend_list(self):
        self.update_progress(
            1,
            'Collect a list of all your friends'
        )
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
        self.update_progress(
            10,
            'Collecting general information of each of your friends.'
        )
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
                    self.calculate_progress_by_queue(
                        requested,
                        len(api.queued_requests),
                        10,
                        20
                    ),
                    'General information for %s of %s friends already fetched'
                    % (processed_total, requested)
                )

    def fetch_locations(self):

        self.update_progress(
            20,
            'Collecting your and your friends locations.'
        )

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
        fb_location_count = 0
        for responses in generator:
            for response in responses:
                try:
                    person = Person.objects.get(fb_id=response['id'])
                except Person.DoesNotExist:
                    continue
                for fb_location in response['data']:
                    fb_location_count += 1
                    store = Store()
                    store.fb_location_by_person(fb_location, person)

            self.update_progress(
                self.calculate_progress_by_queue(
                    requested,
                    len(api.queued_requests),
                    20,
                    50
                ),
                'Collecting your and your friends locations (%s collected).'
                % fb_location_count
            )

    def fetch_locations_by_fb_id(self):

        self.update_progress(50, 'Complement incomplete location data.')

        requests = []
        locations = Location.objects.filter(
            fb_id__isnull=False,
            longitude__isnull=True,
            latitude__isnull=True
        )
        for location in locations:
            requests.append({
                'id': str(location.fb_id),
                'request': str(location.fb_id)
            })
        api = Api(self.person.access_token)
        requested = len(requests)
        generator = api.request(requests)
        fb_location_count = 0
        for responses in generator:
            for response in responses:
                try:
                    locations = Location.objects.filter(fb_id=response['id'])
                except Location.DoesNotExist:
                    continue
                fb_location_count += 1
                store = Store()
                store.fb_location_by_locations(response['data'], locations)

            self.update_progress(
                self.calculate_progress_by_queue(
                    requested,
                    len(api.queued_requests),
                    50,
                    80
                ),
                'Complement incomplete location data (%s complemented).'
                % fb_location_count
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
                store = Store()
                store.geo_data(response)


    def store_distances(self):
        self.update_progress(
            80,
            "Calculating distances between all hometows.")
        self.store_distances_between_hometowns()
        self.update_progress(
            90,
            "Calculating travel distances for you and each of your friends."
        )
        self.store_distances_from_hometowns()
        self.update_progress(
            100,
            "Creating a report based on all collected information."
        )

    def store_distances_between_hometowns(self):
        locations = Location.objects.filter(
            hometown_distance__isnull=True,
            type='H'
        )
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
        locations = Location.objects.filter(
            travel_distance__isnull=True,
            type='P'
        )
        for location in locations:
            try:
                hometown = Location.objects.get(
                    type='H',
                    person_id=location.person_id
                )
            except Location.DoesNotExist:
                continue
            distance = fb.geo.distance(
                location.longitude,
                location.latitude,
                hometown.longitude,
                hometown.latitude
            )
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