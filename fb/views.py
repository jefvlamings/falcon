from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from facebook import Api, User, Auth
from models import Person


# IndexView
class IndexView(View):

    # Get
    def get(self, request, id=0):
        access_token = get_access_token_by_person(id)
        if access_token is not None:
            user = User(id, access_token)
            return render(
                request,
                'index.html',
                {
                    'user': user
                }
            )
        else:
            return redirect('/facebook/connect')


# CreateView
class CreateView(View):

    access_token = None
    user_id = None

    # Get
    def get(self, request, *args, **kwargs):
        if self.user_is_accessible(request) is True:
            self.fetch_data()
            return HttpResponse()
        else:
            return HttpResponseNotFound()

    # Check if user is accesible
    def user_is_accessible(self, request):
        if 'user_id' in request.GET:
            self.user_id = request.GET['user_id']
            self.access_token = get_access_token_by_person(self.user_id)
            if self.access_token is not None:
                return True
            else:
                return True
        else:
            return False

    # Fetch Data
    def fetch_data(self):

        # Fetch and store the user
        user = User(self.user_id, self.access_token)
        self.store_user(user)

        # Fetch and store its friends
        friends = user.friends
        for friend in friends:
            self.store_user(friend)

    # Store User data
    def store_user(self, fb_user):
        try:
            person = Person.objects.get(id=fb_user.id)
        except Person.DoesNotExist:
            person = Person.objects.create(id=fb_user.id)

        person.first_name = fb_user.first_name
        # person.middle_name = fb_user.middle_name
        person.last_name = fb_user.last_name
        # person.gender = fb_user.gender
        # person.birthday = fb_user.birthday
        # person.address = fb_user.home_town
        # person.significant_other = fb_user.significant_other_id
        # person.relationship_status = fb_user.relationship_status
        person.save()


# ReportView
class ReportView(View):

    # Get
    def get(self, request, user_id):
        person = Person.objects.get(id=user_id)
        return render(
            request,
            'report.html',
            {
                'person': person
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
                    id=user_id,
                    access_token=access_token,
                )
                person.save()
                return redirect('/facebook/' + str(user_id))
            else:
                return HttpResponse('Something went wrong will validating the facebook access_token')
        else:
            url = auth.get_access_url()
            return redirect(url)


# Helper functions
def get_access_token_by_person(person_id):

    try:
        person = Person.objects.get(id=person_id)
    except Person.DoesNotExist:
        person = None

    if person is not None and person.access_token is not '':
        auth = Auth()
        if auth.validate_access_token(person.access_token) is True:
            return person.access_token
        else:
            return None
    else:
        return None