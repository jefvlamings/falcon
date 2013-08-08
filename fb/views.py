from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from facebook import User, Auth
from models import Person
import datetime


# IndexView
class IndexView(View):

    # Get
    def get(self, request, id=None):
        try:
            person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return redirect('/connect')
        if person.access_token is not None:
            print person.fb_id
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


# CreateView
class CreateView(View):

    person = None

    # Get
    def get(self, request, id):
        try:
            person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()
        self.person = person
        if person.access_token is not None:
            self.fetch_data()
        else:
            return HttpResponseNotFound
        return HttpResponse()

    # Fetch Data
    def fetch_data(self):

        # Fetch and store the user
        user = User(self.person.fb_id, self.person.access_token)
        self.store_user(user)

        # Fetch and store its friends
        friends = user.friends
        for friend in friends:
            self.store_user(friend)

    # Store User data
    def store_user(self, fb_user):
        try:
            person = Person.objects.get(fb_id=fb_user.id)
        except Person.DoesNotExist:
            person = Person.objects.create(fb_id=fb_user.id)

        person.add_relationship(self.person)
        person.first_name = fb_user.first_name
        person.middle_name = fb_user.middle_name
        person.last_name = fb_user.last_name
        person.gender = fb_user.gender
        person.birthday = fb_user.birthday
        person.address = fb_user.home_town
        person.significant_other = fb_user.significant_other_id
        person.relationship_status = fb_user.relationship_status
        person.save()


# ReportView
class ReportView(View):

    # Get
    def get(self, request, id):
        try:
            person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        return render(
            request,
            'report.html',
            {
                'person': person,
                'youngest_friends': person.friends().order_by('birthday').reverse()[:5],
                'oldest_friends': person.friends().exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(birthday__isnull=False).order_by('birthday')[:5]
            }
        )


# ConnectView
class ConnectView(View):

    # Get
    def get(self, request, *args, **kwargs):
        auth = Auth()
        if 'code' in request.GET:
            code = request.GET['code']
            access_token = auth.get_access_token(code)
            if auth.validate_access_token(access_token) is True:
                user_id = auth.get_user_id(access_token)
                person = Person(
                    fb_id=user_id,
                    access_token=access_token,
                )
                person.save()
                return redirect('/facebook/' + str(person.pk))
            else:
                return HttpResponse('Something went wrong will validating the facebook access_token')
        else:
            url = auth.get_access_url()
            return redirect(url)