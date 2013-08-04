from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from facebook import User, Auth
from models import Person


# IndexView
class IndexView(View):

    # Get
    def get(self, request, id=0):
        user = User(id)
        return render(
            request,
            'index.html',
            {
                'user': user
            }
        )


# CreateView
class CreateView(View):

    # Get
    def get(self, request, *args, **kwargs):
        if self.request_is_valid(request):
            if self.fetch_data(request.GET['user_id']):
                return HttpResponse()
            else:
                return HttpResponseNotFound()
        else:
            return HttpResponseNotFound()

    # Validate request
    def request_is_valid(self, request):
        if 'user_id' in request.GET and 'hash' in request.GET:
            if request.GET['hash'] == 'hello':
                return True
            else:
                return False
        else:
            return False

    # Fetch Data
    def fetch_data(self, user_id):

        # Fetch and store the user
        user = User(user_id)
        self.store_user(user)

        # Fetch and store all of its friends
        # friends = user.friends
        # for friend in friends:
        #     self.store_user(friend)

        return True

    # Store User data
    def store_user(self, fb_user):
        person = Person.objects.get(id=fb_user.id)
        person.first_name = fb_user.first_name
        person.middle_name = fb_user.middle_name
        person.last_name = fb_user.last_name
        person.gender = fb_user.gender
        person.birthday = fb_user.birthday
        person.address = fb_user.home_town
        person.significant_other = fb_user.significant_other_id
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
                print user_id
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
