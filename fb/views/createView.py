from django.views.generic.base import View
from django.http import HttpResponse, HttpResponseNotFound
from fb.facebook import User
from fb.geo import Mapquest
from fb.models import Person, Location
from celery import task


class CreateView(View):

    person = None

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


    @task()
    def fetch_data(self):

        # Fetch and store the user
        user = User(self.person.fb_id, self.person.access_token)
        self.store_user(user)

        # Fetch and store its friends
        friends_processed = 0
        for fb_friend in user.friends:
            friend = User(fb_friend['id'], self.person.access_token)
            self.store_user(friend)
            friends_processed += 1
            self.person.progress = (float(friends_processed)/len(user.friends))*100
            self.person.save()

        # Fetch and store coordinates
        self.fetch_coordinates()

    def store_user(self, fb_user):

        # Check if this a Person exsists for this facebook user id, otherwise create one
        try:
            person = Person.objects.get(fb_id=fb_user.id)
        except Person.DoesNotExist:
            person = Person.objects.create(fb_id=fb_user.id)

        # Set properties to the object
        person.add_relationship(self.person)
        person.first_name = fb_user.first_name
        person.middle_name = fb_user.middle_name
        person.last_name = fb_user.last_name
        person.gender = fb_user.gender
        person.birthday = fb_user.birthday
        person.significant_other = fb_user.significant_other_id
        person.relationship_status = fb_user.relationship_status
        person.save()

        if person.fb_id == self.person.fb_id:
            self.person = person

        # Store hometown
        if fb_user.home_town is not None:
            try:
                location = Location.objects.get(person_id=person.id, type='H')
            except Location.DoesNotExist:
                location = Location.objects.create(person_id=person.id, type='H')
            location.name = fb_user.home_town
            location.save()

        # Store locations
        if fb_user.locations is not None:
            for fb_location in fb_user.locations:
                try:
                    location = Location.objects.get(person_id=person.id, type='P', name=fb_location['name'])
                except Location.DoesNotExist:
                    location = Location.objects.create(person_id=person.id, type='P')
                location.name = fb_location['name']
                location.latitude = fb_location['latitude']
                location.longitude = fb_location['longitude']
                location.save()

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