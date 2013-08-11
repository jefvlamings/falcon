from django.views.generic.base import View
from django.shortcuts import redirect
from django.http import HttpResponse
from fb.facebook import Auth
from fb.models import Person


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