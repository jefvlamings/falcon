from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponseNotFound
from fb.models import Person, Location
from django.db.models import Max
import datetime


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
                    'youngest_friends': self.get_five_youngest_friends(),
                    'oldest_friends': self.get_five_oldest_friends(),
                    'male_ages': self.get_male_ages(),
                    'female_ages': self.get_female_ages(),
                    'male_relationships': self.get_male_relationships(),
                    'female_relationships': self.get_female_relationships()
                }
            )

    def get_five_youngest_friends(self):
        friends = self.person.friends.order_by('birthday').reverse()[:5]
        return friends

    def get_five_oldest_friends(self):
        friends = self.person.friends.exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(birthday__isnull=False).order_by('birthday')[:5]
        return friends

    def get_male_ages(self):
        ages = []
        male_friends = self.person.friends.exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(gender='M',birthday__isnull=False)
        for male_friend in male_friends:
            ages.append(male_friend.age)
        return ages

    def get_female_ages(self):
        ages = []
        female_friends = self.person.friends.exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(gender='F',birthday__isnull=False)
        for female_friend in female_friends:
            ages.append(female_friend.age)
        return ages

    def get_male_relationships(self):
        output = []
        male_friends = self.person.friends.filter(relationship_status__isnull=False, gender='M')
        for male_friend in male_friends:
            output.append(str(male_friend.relationship_status))
        return output

    def get_female_relationships(self):
        output = []
        female_friends = self.person.friends.filter(relationship_status__isnull=False, gender='F')
        for female_friend in female_friends:
            output.append(str(female_friend.relationship_status))
        return output