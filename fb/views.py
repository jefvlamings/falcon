from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from facebook import User, Auth
from geo import Mapquest
from models import Person, Location
import datetime
import json


class IndexView(View):

    def get(self, request, id=None):

        """
        The access_code for API calls is stored in the Person database. If no person could be found we should we should
        first obtain the access_code via the connect view.
        """
        try:
            person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return redirect('/connect')

        # Check if the access token has been set
        if person.access_token is not None:

            # Show some basic user info
            user = User(person.fb_id, person.access_token)
            return render(
                request,
                'index.html',
                {
                    'user': user,
                    'person': person
                }
            )
        else:
            return redirect('/connect')


class ConnectView(View):

    def get(self, request, *args, **kwargs):

        """
        If an access_code has been given, we should make a request to get the access_token from it. If no access_code
        was given, we should first ask for one
        """

        auth = Auth()

        # Check if a code had been provided in the request
        if 'code' in request.GET:

            # Request and validate an access_token for a given access_code
            code = request.GET['code']
            access_token = auth.get_access_token(code)
            if auth.validate_access_token(access_token) is True:
                user_id = auth.get_user_id(access_token)

                # First check if a Person already exists for this facebook user id
                try:
                    person = Person.objects.get(fb_id=user_id)
                except Person.DoesNotExist:
                    person = Person.objects.create(fb_id=user_id)

                # Store the access_token in the Person db
                person.access_token = access_token
                person.save()

                # Redirect the user to notify if all went well
                return redirect('/facebook/' + str(person.pk))

            # Something went wrong message
            else:
                return HttpResponse('Something went wrong will validating the facebook access_token')

        # Request an access code
        else:
            url = auth.get_access_url()
            return redirect(url)


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