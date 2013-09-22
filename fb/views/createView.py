from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.facebook import Api
from fb.geo import Mapquest
from fb.models import Person, Location, Progress, Relationship
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
            self.fetch_data()
        else:
            return HttpResponseNotFound
        return HttpResponse()

    def fetch_data(self):
        self.start_progress()
        self.fetch_friend_list()
        self.fetch_user_data()
        self.fetch_mutual_friends()
        self.store_mutual_friend_count()
        self.fetch_posts()
        self.fetch_locations()
        self.fetch_locations_by_fb_id()
        self.store_distances()

    def start_progress(self):
        """
        We continuously monitor the data fetching progress. This function makes
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
        """
        Fetches the Facebook ID for each friend. A Person object is created for
        each friend to store this Facebook ID. The ID will be used to counter
        reference future API calls.
        """
        requests = [{
            'id': self.person.fb_id,
            'request': str(self.person.fb_id) + '/friends'
        }]
        progress = {
            'from': 1, 'to': 10,
            'description': 'Collecting a list of all your friends'
        }
        self.store_api_response('friend_list', requests, progress)

    def fetch_user_data(self):
        """
        Fetches basic user information, containing data like name, gender, age,
        etc., for each friend of the current person. This information is added
        to an earlier created Person object for each friend
        """
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id)
            })
        progress = {
            'from': 10, 'to': 15,
            'description': 'Collecting general information of each of your '
                           'friends'
        }
        self.store_api_response('user_data', requests, progress)

    def fetch_mutual_friends(self):
        """
        Fetches all mutual connections between the current person and each of
        its friends. These connections are stored as relationships
        """
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(self.person.fb_id) + '/mutualfriends/' + str(friend.fb_id)
            })
        progress = {
            'from': 15, 'to': 20,
            'description': 'Collecting data about mutual friends'
        }
        self.store_api_response('mutual_friends', requests, progress)

    def store_mutual_friend_count(self):
        """
        Count for each friend how many mutual friends the current person has.
        This number is stored in the relationship table
        """
        friends = self.person.friends
        for friend in friends:
            mutual_friend_count = 0
            second_degree_friends = friend.friends
            for second_degree_friend in second_degree_friends:
                if second_degree_friend in friends:
                    mutual_friend_count += 1
            try:
                relationship = Relationship.objects.get(
                    from_person=self.person, to_person=friend
                )
            except Relationship.DoesNotExist:
                continue

            relationship.mutual_friend_count = mutual_friend_count
            relationship.save()

    def fetch_posts(self):
        """
        Fetches all posts from each friend (including self). A Post object
        will be created for each post to store the fetched data
        """
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id) + '/posts'
            })
        progress = {
            'from': 20, 'to': 50,
            'description': 'Collecting your and your friends posts'
        }
        self.store_api_response('posts', requests, progress)

    def fetch_locations(self):
        """
        Fetches all locations for each friend (including self). A Location
        object will be created to store the longitude and langitude of each
        location
        """
        requests = []
        friends = self.person.friends
        for friend in friends:
            requests.append({
                'id': friend.fb_id,
                'request': str(friend.fb_id) + '/locations'
            })
        progress = {
            'from': 50, 'to': 80,
            'description': 'Collecting your and your friends locations'
        }
        self.store_api_response('locations', requests, progress)

    def fetch_locations_by_fb_id(self):
        """
        Fetches all locations for which we have a Facebook ID in the database
        but no coordinates yet. Primarily used to complement Location date for
        hometowns which are fetched earlier but without coordinates.
        """
        requests = []
        locations = Location.objects.filter(
            fb_id__isnull=False, longitude__isnull=True, latitude__isnull=True
        )
        for location in locations:
            requests.append({
                'id': str(location.fb_id),
                'request': str(location.fb_id)
            })
        progress = {
            'from': 80, 'to': 90,
            'description': 'Complement incomplete location data'
        }
        self.store_api_response('locations_by_fb_id', requests, progress)

    def store_api_response(self, type, requests, progress):
        """
        Storing API responses first starts with fetching the data from the
        API and storing it using the correct storage (Store) function for the
        type of request. During this process, progress information is collected
        and stored as well.
        """
        self.update_progress(progress['from'], progress['description'])
        api = Api(self.person.access_token)
        requested = len(requests)
        generator = api.request(requests)
        for responses in generator:
            for response in responses:
                store = Store()
                if type is 'friend_list':
                    store.fb_relationship(response, self.person)
                elif type is 'user_data':
                    store.user(response, self.person)
                elif type is 'mutual_friends':
                    store.mutual_friends(response)
                elif type is 'posts':
                    store.fb_posts(response)
                elif type is 'locations':
                    store.fb_locations(response, 'person')
                elif type is 'locations_by_fb_id':
                    store.fb_locations(response, 'location')
            queued = len(api.queued_requests)
            processed_total = requested - queued
            self.update_progress(
                self.calculate_progress_by_queue(
                    requested, queued, progress['from'],
                    progress['to']
                ),
                progress['description'] +
                ' (%s/%s).' % (processed_total, requested)
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
        """
        Calculates distances between different kinds of locations
        """
        self.update_progress(
            90,
            "Calculating distances between all hometowns.")
        self.store_distances_between_hometowns()
        self.update_progress(
            95,
            "Calculating travel distances for you and each of your friends."
        )
        self.store_distances_from_hometowns()
        self.update_progress(
            100,
            "Creating a report based on all collected information."
        )

    def store_distances_between_hometowns(self):
        """
        Calculates the distances between the current persons' hometown and
        those of its friends one by one. The location is added to the Location
        object
        """
        locations = Location.objects.filter(
            hometown_distance__isnull=True,
            type='H'
        )
        for location in locations:
            distance = fb.geo.distance(
                location.longitude, location.latitude,
                self.person.hometown.longitude, self.person.hometown.latitude
            )
            location.hometown_distance = distance
            location.save()

    def store_distances_from_hometowns(self):
        """
        Calculates the distances between each persons' hometown and all of its
        other locations. This information will be used to indicate travel
        distances
        """
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
                location.longitude, location.latitude, hometown.longitude,
                hometown.latitude
            )
            location.travel_distance = distance
            location.save()

    def update_progress(self, percentage, description):
        """
        Helper function to quickly update the progress of the current report
        """
        self.progress.percentage = percentage
        self.progress.description = description
        self.progress.save()

    def calculate_progress_by_queue(self, total, togo, begin, end):
        """
        Algorithm to calculate the completion percentage
        """
        progress_range = float(end) - float(begin)
        percentage = float(begin) + (((float(total) - float(togo)) / float(total)) * float(progress_range))
        return percentage