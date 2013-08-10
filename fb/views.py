from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from facebook import User, Auth
from geo import Mapquest
from models import Person, Location
import datetime


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
                    'user': user
                }
            )
        else:
            return redirect('/connect')


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

        # # Fetch and store its friends
        # friends = user.friends
        # for friend in friends:
        #     self.store_user(friend)

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

        # Store hometown
        if fb_user.home_town is not None:
            try:
                location = Location.objects.get(person_id=person.id, type='H')
            except Location.DoesNotExist:
                location = Location.objects.create(person_id=person.id, type='H')
            location.name = fb_user.home_town
            location.save()

    def fetch_coordinates(self):

        # To-do: group same locations...

        locations = Location.objects.filter(latitude__isnull=True)
        location_names = []
        for location in locations:
            location_names.append(location.name)

        mapquest = Mapquest()
        geo_data = mapquest.batch_request_names(location_names)
        self.store_coordinates(geo_data)

    def store_coordinates(self, geo_data):
        for geo_entry in geo_data:
            try:
                locations = Location.objects.filter(name=geo_entry['providedLocation']['location'])
            except Location.DoesNotExist:
                continue

            for location in locations:
                location.latitude = geo_entry['locations'][0]['latLng']['lat']
                location.longitude = geo_entry['locations'][0]['latLng']['lng']
                location.save()






class ReportView(View):

    def get(self, request, id):

        # First check if a Person exists for this id
        try:
            person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # Render the report to 'report.html'
        return render(
            request,
            'report.html',
            {
                'person': person,
                'youngest_friends': person.friends().order_by('birthday').reverse()[:5],
                'oldest_friends': person.friends().exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(birthday__isnull=False).order_by('birthday')[:5]
            }
        )


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