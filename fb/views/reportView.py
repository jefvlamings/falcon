from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponseNotFound
from fb.models import Person, Progress, Relationship
import datetime


class ReportView(View):

    person = None
    progress = None

    def get(self, request, id):

        # First check if a Person exists for this id
        try:
            self.person = Person.objects.get(pk=id)
        except Person.DoesNotExist:
            return HttpResponseNotFound()

        # First check if a Progress exists for this person
        try:
            self.progress = Progress.objects.get(person=self.person)
        except Progress.DoesNotExist:
            return HttpResponseNotFound()

        # If the report is not yet ready, show a status of the report
        if self.progress.percentage < 100:
            return render(
                request,
                'status.html',
                {
                    'person': self.person,
                    'progress': self.progress,
                }
            )
        # Show the report
        else:
            return render(
                request,
                'report.html',
                {
                    'person': self.person,
                    'friends': len(self.person.friends),
                    'male_ages': self.get_ages('M'),
                    'female_ages': self.get_ages('F'),
                    'average_male_age': self.get_average_age('M'),
                    'average_female_age': self.get_average_age('F'),
                    'youngest_friends': self.friends_ordered_by_age(None, 'ASC', 5),
                    'oldest_friends': self.friends_ordered_by_age(None, 'DESC', 5),
                    'youngest_male': self.friends_ordered_by_age('M', 'ASC')[0],
                    'youngest_female': self.friends_ordered_by_age('F', 'ASC')[0],
                    'oldest_male': self.friends_ordered_by_age('M', 'DESC')[0],
                    'oldest_female': self.friends_ordered_by_age('F', 'DESC')[0],
                    'male_relationships': self.get_relationships('M'),
                    'female_relationships': self.get_relationships('F'),
                    'top_connected_friends': self.friends_ordered_by_mutual_friend_count(None, 'DESC', 5),
                    'least_connected_friends': self.friends_ordered_by_mutual_friend_count(None, 'ASC', 5),
                    'male_connections': self.get_connections('M'),
                    'female_connections': self.get_connections('F')
                }
            )

    def friends_ordered_by_age(self, gender=None, order='ASC', limit=1):
        friends = self.person.friends.exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(birthday__isnull=False)
        if gender is not None:
            friends = friends.filter(gender=gender)
        friends = friends.order_by('-birthday')
        if order is not 'ASC':
            friends = friends.reverse()
        return friends[:limit]

    def get_average_age(self, gender):
        ages = self.get_ages(gender)
        return reduce(lambda x, y: x + y, ages) / len(ages)

    def get_ages(self, gender):
        ages = []
        friends = self.person.friends.exclude(birthday__lt=datetime.date(1901, 1, 1)).filter(gender=gender,birthday__isnull=False)
        for friend in friends:
            ages.append(friend.age)
        return ages

    def get_relationships(self, gender):
        output = []
        friends = self.person.friends.filter(relationship_status__isnull=False, gender=gender)
        for friend in friends:
            output.append(str(friend.relationship_status))
        return output

    def get_connections(self, gender):
        friends = self.friends_ordered_by_mutual_friend_count(gender, 'ASC', 1)
        totals = []
        for friend in friends:
            totals.append(friend.mutual_friend_count)
        return totals

    def friends_ordered_by_mutual_friend_count(self, gender=None, order='ASC', limit=1):
        friends = self.person.connected_friends(gender, order, limit)
        return friends