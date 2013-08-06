import requests
import datetime
import urlparse
from models import Person

# Constants
APP_ID = '160902533967876'
APP_SECRET = 'e2bdd68bedc3243e3a1dbdaf02c81564'
REDIRECT_URI = 'http://127.0.0.1:8000/connect/'
SCOPE = 'publish_stream, ' \
        'user_online_presence, ' \
        'friends_online_presence, ' \
        'manage_pages, ' \
        'read_page_mailboxes, ' \
        'photo_upload, ' \
        'ads_management, ' \
        'read_stream, ' \
        'export_stream, ' \
        'status_update, ' \
        'share_item, ' \
        'sms, read_friendlists, ' \
        'manage_friendlists, ' \
        'create_note, ' \
        'create_event, ' \
        'rsvp_event, ' \
        'read_insights, ' \
        'xmpp_login ,' \
        'read_mailbox, ' \
        'manage_notifications, ' \
        'read_requests, ' \
        'video_upload, ' \
        'user_birthday, ' \
        'friends_birthday'


# Authentication
class Auth:

    # Get Access URL
    def get_access_url(self):
        return 'https://www.facebook.com/dialog/oauth' \
               '?client_id=' + APP_ID + \
               '&redirect_uri=' + REDIRECT_URI + \
               '&scope=' + SCOPE

    # Get Access Token
    def get_access_token(self, code):
        url = 'https://graph.facebook.com/oauth/access_token' + \
              '?client_id=' + APP_ID + \
              '&client_secret=' + APP_SECRET + \
              '&redirect_uri=' + REDIRECT_URI + \
              '&code=' + code
        response = requests.get(url)
        params = urlparse.parse_qs(response.content)
        if 'access_token' in params:
            return params['access_token'][0]
        else:
            return None

    # Get App Token
    def get_app_token(self):
        url = 'https://graph.facebook.com/oauth/access_token' + \
              '?client_id=' + APP_ID + \
              '&client_secret=' + APP_SECRET + \
              '&redirect_uri=' + REDIRECT_URI + \
              '&grant_type=client_credentials'
        response = requests.get(url)
        params = urlparse.parse_qs(response.content)
        if 'access_token' in params:
            return params['access_token'][0]
        else:
            return None

    # Debug Access Token
    def debug_access_token(self, access_token):
        auth = Auth()
        app_token = auth.get_app_token()
        url = 'https://graph.facebook.com/debug_token' \
              '?input_token=' + access_token + \
              '&access_token=' + app_token
        response = requests.get(url).json()
        return response

    # Validate access_token
    def validate_access_token(self, access_token):
        debug_data = self.debug_access_token(access_token)
        if 'data' in debug_data:
            return debug_data['data']['is_valid']
        else:
            return False

    # Get Valid User Id
    def get_user_id(self, access_token):
        debug_data = self.debug_access_token(access_token)
        if 'data' in debug_data:
            return debug_data['data']['user_id']
        else:
            return None


# Api
class Api:

    access_token = ''

    def __init__(self, access_token):
        self.access_token = access_token

    def connect(self):
        try:
            person = Person.objects.get(id=self.id)
        except Person.DoesNotExist:
            person = None

        if person is not None and person.access_token is not '':
            auth = Auth()
            return auth.validate_access_token(person.access_token)
        else:
            return False

    def user(self, user_id=None):
        if user_id is None:
            user_id = 'me'
        return self.request(str(user_id))

    def user_id(self):
        return self.user()['id']

    def request(self, request):
        url = 'https://graph.facebook.com/' + str(request) + '?access_token=' + str(self.access_token)
        response = requests.get(url).json()
        if 'paging' in response:
            data = response['data']
            nextURL = response['paging']['next']
            data += self.batch_request(nextURL)
        else:
            data = response
        return data

    def batch_request(self, url):
        response = requests.get(url).json()
        data = response['data']
        if 'paging' in response:
            batch = response['paging']
            if 'next' in batch:
                nextURL = batch['next']
                data += self.batch_request(nextURL)

        return data

    def friends(self, user_id=None):
        if user_id is None:
            user_id = self.user_id()
        return self.request(str(user_id) + '/friends')

    def statuses(self, user_id=None):
        if user_id is None:
            user_id = self.user_id()
        return self.request(str(user_id) + '/statuses')

    def likes(self, object):
        if 'likes' in object:
            likes = object['likes']
            data = object['likes']['data']
            if 'paging' in likes:
                batch = likes['paging']
                if 'next' in batch:
                    nextURL = batch['next']
                    data += self.batch_request(nextURL)
        else:
            data = {}
        return data

    def number_of_likes(self, object):
        likes = self.likes(object)
        return len(likes)

    def locations(self, user_id=None):
        if user_id is None:
            user_id = self.user_id()
        return self.request(str(user_id) + '/locations')


# User
class User:

    id = None
    api = None
    fb_user = None
    access_token = None

    def __init__(self, id, access_token):
        self.api = Api(access_token)
        self.access_token = access_token
        self.id = id
        self.fb_user = self.api.user(id)

    @property
    def name(self):
        return self.fb_user['name']

    @property
    def first_name(self):
        if 'first_name' in self.fb_user:
            return self.fb_user['first_name']
        else:
            return ''

    @property
    def middle_name(self):
        if 'middle_name' in self.fb_user:
            return self.fb_user['middle_name']
        else:
            return ''

    @property
    def last_name(self):
        if 'last_name' in self.fb_user:
            return self.fb_user['last_name']
        else:
            return ''

    @property
    def gender(self):
        if 'gender' in self.fb_user:
            gender = self.fb_user['gender']
            if gender == 'male':
                return 'M'
            elif gender == 'female':
                return 'F'
            else:
                return 'X'
        else:
            return 'X'

    @property
    def home_town(self):
        if 'hometown' in self.fb_user:
            return self.place_name(self.fb_user['hometown'])
        else:
            return None

    @property
    def significant_other_id(self):
        if 'significant_other' in self.fb_user:
            return self.fb_user['significant_other']['id']
        else:
            return None

    @property
    def birthday(self):
        if 'birthday' in self.fb_user:
            birthday = self.fb_user['birthday']
            date_items_count = len(birthday.split('/'))
            if date_items_count is 1:
                format = '%m'
            elif date_items_count is 2:
                format = '%m/%d'
            elif date_items_count is 3:
                format = '%m/%d/%Y'
            return datetime.datetime.strptime(birthday, format)
        else:
            return None

    @property
    def relationship_status(self):
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
        if 'relationship_status' in self.fb_user:
            status = self.fb_user['relationship_status'].lower()
            return statuses[status]
        else:
            return 'X'

    @property
    def statuses(self):
        statuses = self.api.statuses(self.id)
        output = []
        for status in statuses:
            output.append(self.summarize_status(status))
        return output

    @property
    def friends(self):
        fb_friends = self.api.friends(self.id)
        friends = []
        for fb_friend in fb_friends:
            friend = User(fb_friend['id'], self.access_token)
            friends.append(friend)
        return friends

    def summarize_status(self, status):
        output = {
            'message': '',
            'number_of_likes': self.api.number_of_likes(status),
            'date': None,
            'place': None
        }
        if 'message' in status:
            output['message'] = status['message']
        if 'updated_time' in status:
            date = status['updated_time']
            new_date = date[:19] # Only the 19 first characters will be used
            output['date'] = datetime.datetime.strptime(new_date, "%Y-%m-%dT%H:%M:%S")
        if 'place' in status:
            output['place'] = status['place']
        return output

    def place_name(self, place):
        if 'name' in place:
            return place['name']
        else:
            return ''