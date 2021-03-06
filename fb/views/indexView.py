from django.views.generic.base import View
from django.shortcuts import render, redirect
from fb.models import Person


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
        if person.access_token is None:
            return redirect('/connect')

        return render(
            request,
            'index.html',
            {
                'person': person
            }
        )