import datetime
from django.utils.timezone import utc
from models import Person, Location, Post


class Store():

    def fb_posts(self, response):
        for fb_post in response['data']:
            self.fb_post(fb_post)

    def fb_post(self, response):
        """
        Get or create a post for each result in the response data.
        """
        fb_post = self.process_post(response)
        if fb_post is None:
            return
        try:
            post = Post.objects.get(fb_id=fb_post['id'])
        except Post.DoesNotExist:
            post = Post.objects.create(from_person_id=fb_post['from_person_id'])
        post.fb_id = fb_post['id']
        post.message = fb_post['message']
        post.picture = fb_post['picture']
        post.link = fb_post['link']
        post.like_count = fb_post['like_count']
        post.created_time = fb_post['created_time']
        post.save()

    def process_post(self, data):
        """
        Distill all relevant information from the API response data in two
        steps. First the essential information is processed. If one of the
        required items doesn't exist, we return None. In the second step
        additional information is processed
        """
        post = {}

        # 1. Essential information
        try:
            post['from_fb_id'] = data['from']['id']
            post['id'] = data['id']
            post['created_time'] = datetime.datetime.strptime(data['created_time'][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=utc)
        except (KeyError, TypeError):
            return None

        # 1.1. Try to fetch the person for this fb_id
        try:
            person = Person.objects.get(fb_id=post['from_fb_id'])
        except Person.DoesNotExist:
            return None

        # 2. Additional information
        if 'likes' in data:
            post['like_count'] = data['likes'].get('count', 0)
        else:
            post['like_count'] = 0
        if 'message' in data:
            post['message'] = data['message']
        elif 'story' in data:
            post['message'] = data['story']
        elif 'caption' in data:
            post['message'] = data['caption']
        elif 'name' in data:
            post['message'] = data['name']
        else:
            post['message'] = ''
        post['picture'] = data.get('picture', None)
        post['link'] = data.get('link', None)
        post['from_person_id'] = person.id

        return post

    def geo_data(self, geo_data):

        # Get all locations from the db that have the same name as the current
        # location name
        try:
            locations = Location.objects.filter(name=geo_data['providedLocation']['location'])
            location_data = geo_data['locations'][0]
        except (Location.DoesNotExist, KeyError, IndexError):
            return None

        # Set the coordinates and save the location
        for location in locations:
            try:
                location.latitude = location_data['latLng']['lat']
                location.longitude = location_data['latLng']['lng']
                location.street = location_data['street']
                location.postal_code = location_data['postalCode']
                # location.city = location_data['adminArea5']
                location.country = location_data['adminArea1']
            except (IndexError, KeyError):
                continue
            location.save()

    def fb_locations(self, response, type):
        if type is 'person':
            try:
                person = Person.objects.get(fb_id=response['id'])
                for fb_location in response['data']:
                    self.fb_location_by_person(fb_location, person)
            except Person.DoesNotExist:
                return
        if type is 'location':
            try:
                locations = Location.objects.filter(fb_id=response['id'])
                self.fb_location_by_locations(response['data'], locations)
            except Location.DoesNotExist:
                return

    def fb_location_by_person(self, response, person):
        fb_location = self.process_location(response)
        if fb_location is None:
            return
        try:
            location = Location.objects.get(person_id=person.id, type='P', name=fb_location['name'])
        except Location.DoesNotExist:
            location = Location.objects.create(person_id=person.id, type='P')
        location.fb_id = fb_location['id']
        location.name = fb_location['name']
        location.latitude = fb_location['latitude']
        location.longitude = fb_location['longitude']
        location.created_time = fb_location['created_time']
        location.save()

    def process_location(self, data):
        location = {}
        try:
            location['id'] = data['id']
            location['name'] = data['place']['name']
            location['latitude'] = data['place']['location']['latitude']
            location['longitude'] = data['place']['location']['longitude']
            location['created_time'] = datetime.datetime.strptime(data['created_time'][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=utc)
        except (KeyError, TypeError):
            return None
        return location

    def fb_location_by_locations(self, response, locations):
        fb_location = self.process_fb_location(response)
        if fb_location is None:
            return
        for location in locations:
            location.name = fb_location['name']
            location.latitude = fb_location['latitude']
            location.longitude = fb_location['longitude']
            location.save()

    def process_fb_location(self, data):
        location = {}
        try:
            location['id'] = data['id']
            location['name'] = data['name']
            location['latitude'] = data['location']['latitude']
            location['longitude'] = data['location']['longitude']
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

    def user(self, response, person):
        user = self.process_user(response['data'])
        try:
            friend = Person.objects.get(fb_id=response['id'])
        except Person.DoesNotExist:
            friend = Person.objects.create(fb_id=response['id'])
        friend.add_relationship(person)
        friend.first_name = user['first_name']
        friend.middle_name = user['middle_name']
        friend.last_name = user['last_name']
        friend.gender = user['gender']
        friend.birthday = user['birthday']
        friend.significant_other = user['significant_other']
        friend.relationship_status = user['relationship_status']

        if user['hometown_id'] is not None:
            self.hometown(user['hometown_id'], friend)

        friend.save()
        return friend

    def mutual_friends(self, response):
        try:
            person = Person.objects.get(fb_id=response['id'])
        except Person.DoesNotExist:
            return
        for fb_friend in response['data']:
            self.relationship(fb_friend, person)

    def fb_relationship(self, response, person):
        for friend in response['data']:
            try:
                friend = Person.objects.get(fb_id=friend['id'])
            except Person.DoesNotExist:
                friend = Person.objects.create(fb_id=friend['id'])
            friend.add_relationship(person)
            friend.save()

    def relationship(self, fb_friend, person):
        try:
            friend = Person.objects.get(fb_id=fb_friend['id'])
            person.add_relationship(friend)
        except Person.DoesNotExist:
            return None

    def hometown(self, id, person):
        try:
            location = Location.objects.get(person_id=person.id, type='H')
        except Location.DoesNotExist:
            location = Location.objects.create(person_id=person.id, type='H')
        location.fb_id = id
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
        user['hometown_id'] = hometown.get('id', None)
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