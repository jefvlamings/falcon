from django.views.generic.base import View
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from facebook import User, Auth
from models import Person


# IndexView
class IndexView(View):

    # Get
    def get(self, request, *args, **kwargs):
        user = User()
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
        fb_user = User(user_id)
        person = Person(
            id=user_id,
            first_name=fb_user.first_name,
            middle_name=fb_user.middle_name,
            last_name=fb_user.last_name,
            gender=fb_user.gender,
            birthday=fb_user.birthday,
            address=fb_user.home_town,
            significant_other=fb_user.significant_other_id,
            relationship_status=fb_user.relationship_status,
        )
        person.save()
        return True


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
            auth.set_access_token(code)
            return redirect('facebook/')
        else:
            url = auth.get_access_url()
            return redirect(url)
