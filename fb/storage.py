import datetime
from models import Person, Location


class Store():

    def location(self, response, person):
        fb_location = self.process_location(response)
        if fb_location is None:
            return

        try:
            location = Location.objects.get(person_id=person.id, type='P', name=fb_location['name'])
        except Location.DoesNotExist:
            location = Location.objects.create(person_id=person.id, type='P')
        location.name = fb_location['name']
        location.latitude = fb_location['latitude']
        location.longitude = fb_location['longitude']
        location.save()

    def process_location(self, data):
        location = {}
        try:
            location['name'] = data['place']['name']
            location['latitude'] = data['place']['location']['latitude']
            location['longitude'] = data['place']['location']['longitude']
        except (KeyError, TypeError):
            return None
        return location

    def proces_status(self, data):
        status = {}
        try:
            status['name'] = data['message']
            status['date'] = datetime.datetime.strptime(status['updated_time'][:19], "%Y-%m-%dT%H:%M:%S")
            status['date'] = data['updated_time']
            status['place'] = data['place']
        except (KeyError, TypeError):
            return None
        return status

    def user(self, response, friend):
        user = self.process_user(response['data'])
        try:
            person = Person.objects.get(fb_id=response['id'])
        except Person.DoesNotExist:
            person = Person.objects.create(fb_id=response['id'])
        person.add_relationship(friend)
        person.first_name = user['first_name']
        person.middle_name = user['middle_name']
        person.last_name = user['last_name']
        person.gender = user['gender']
        person.birthday = user['birthday']
        person.significant_other = user['significant_other']
        person.relationship_status = user['relationship_status']

        if user['hometown'] is not None:
            self.hometown(user['hometown'], person)

        person.save()
        return person

    def hometown(self, hometown, person):
        try:
            location = Location.objects.get(person_id=person.id, type='H')
        except Location.DoesNotExist:
            location = Location.objects.create(person_id=person.id, type='H')
        location.name = hometown
        location.save()

    def process_user(self, data):
        user = {}
        user['first_name'] = data.get('first_name', '')
        user['middle_name'] = data.get('middle_name', '')
        user['last_name'] = data.get('last_name', '')
        user['gender'] = self.string_to_gender(data.get('gender', None))
        user['birthday'] = self.string_to_date(data.get('birthday', None))
        significant_other = data.get('significant_other', {})
        user['significant_other'] = significant_other.get('id', None)
        user['relationship_status'] = self.string_to_relationship_status(data.get('relationship_status', ''))
        hometown = data.get('hometown', {})
        user['hometown'] = hometown.get('name', None)
        return user

    def string_to_date(self, string):
        if string is None:
            return None
        else:
            date_items_count = len(string.split('/'))
            if date_items_count is 1:
                format = '%m'
            elif date_items_count is 2:
                format = '%m/%d'
            elif date_items_count is 3:
                format = '%m/%d/%Y'
            return datetime.datetime.strptime(string, format)

    def string_to_gender(self, string):
        if string is None:
            return 'X'
        elif string == 'male':
            return 'M'
        elif string == 'female':
            return 'F'
        else:
            return 'X'

    def string_to_relationship_status(self, string):
        statuses = {
            'single': 'S',
            'in a relationship': 'R',
            'engaged': 'E',
            'married': 'M',
            'it\'s complicated': 'C',
            'in an open relationship': 'O',
            'widowed': 'W',
            'separated': 'X',
            'divorced': 'D',
            'in a civil union': 'U',
            'in a domestic partnership': 'P',
        }
        status = string.lower()
        if status in statuses:
            return statuses[status]
        else:
            return 'X'