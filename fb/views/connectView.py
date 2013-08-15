from django.views.generic.base import View
from django.shortcuts import redirect
from django.http import HttpResponse
from fb.facebook import Auth, Api
from fb.models import Person
from fb.storage import Store


class ConnectView(View):

    person = None
    access_token = None

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
                fb_id = auth.get_user_id(access_token)
                self.access_token = access_token
                self.create_person(fb_id)

                # Redirect the user to notify if all went well
                return redirect('/facebook/' + str(self.person.pk))

            # Something went wrong message
            else:
                return HttpResponse('Something went wrong will validating the facebook access_token')

        # Request an access code
        else:
            url = auth.get_access_url()
            return redirect(url)

    def create_person(self, fb_id):
        try:
            self.person = Person.objects.get(fb_id=fb_id)
        except Person.DoesNotExist:
            self.person = Person.objects.create(fb_id=fb_id)
        self.person.access_token = self.access_token
        self.person.save()
        self.fetch_data(fb_id)

    def fetch_data(self, fb_id):
        api = Api(self.person.access_token)
        request = {
            'id': self.person.fb_id,
            'request': str(self.person.fb_id)
        }
        responses = api.request([request])
        for response in responses:
            store = Store()
            self.person = store.user(response, self.person)