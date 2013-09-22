import requests
import urlparse
from models import Person
import json


# Authentication
class Auth:

    app_id = '160902533967876'
    app_secret = 'e2bdd68bedc3243e3a1dbdaf02c81564'
    redirect_uri = 'http://127.0.0.1:8000/connect/'
    scope = 'publish_stream, ' \
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

    # Get Access URL
    def get_access_url(self):
        return 'https://www.facebook.com/dialog/oauth' \
               '?client_id=' + self.app_id + \
               '&redirect_uri=' + self.redirect_uri + \
               '&scope=' + self.scope

    # Get Access Token
    def get_access_token(self, code):
        url = 'https://graph.facebook.com/oauth/access_token' + \
              '?client_id=' + self.app_id + \
              '&client_secret=' + self.app_secret + \
              '&redirect_uri=' + self.redirect_uri + \
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
              '?client_id=' + self.app_id + \
              '&client_secret=' + self.app_secret + \
              '&redirect_uri=' + self.redirect_uri + \
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
    current_batch = []
    queued_requests = []
    batch_size = 50
    paging_tokens = []
    batch_response_count = 0

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

    def call(self, url):
        response = requests.get(url).json()
        return response

    def request(self, requests):
        self.queued_requests = requests
        while len(self.queued_requests) > 0:
            print 'queued requests: ' + str(len(self.queued_requests))
            print 'paged requests: ' + str(len(self.paging_tokens))
            batch = self.create_batch()
            batch_response = self.batch_request(batch)
            print 'responses in batch: ' + str(self.batch_response_count)
            print '---------------'
            yield batch_response

    def batch_request(self, batch):
        request_url = self.batch_to_request_url(batch)
        self.batch_response_count = 0
        batch_response = self.call(request_url)
        return self.process_batch_response(batch_response)

    def create_batch(self):
        batch = []
        if len(self.queued_requests) > self.batch_size:
            batch += self.queued_requests[-self.batch_size:]
            del self.queued_requests[-self.batch_size:]
        else:
            batch += self.queued_requests
            self.queued_requests = []
        self.current_batch = batch
        return batch

    def process_batch_response(self, batch_response):
        responses = []
        i = 0
        for response in batch_response:
            if response is None:
                continue
            self.validate_response(response)
            data = self.get_data_from_response(response)
            self.batch_response_count += len(data)
            responses.append({
                'id': self.current_batch[i]['id'],
                'request': self.current_batch[i]['request'],
                'data': data
            })
            self.check_data_availability(response)
            i += 1
        return responses

    def validate_response(self, response):
        if not isinstance(response, dict):
            raise Exception('Invalid response: no dictionary is returned')
        elif response['code'] is not 200:
            body = json.loads(response['body'])
            try:
                error_message = body['error']['message']
            except KeyError:
                error_message = body['error_msg']
            raise Exception('Facebook status: [' + str(response['code']) + '] ' + error_message)

    def get_data_from_response(self, response):
        body = json.loads(response['body'])
        if 'data' in body:
            data = body['data']
        else:
            data = body
        return data

    def check_data_availability(self, response):
        body = json.loads(response['body'])
        if 'paging' in body:
            if 'next' in body['paging']:
                self.queue_paged_request(body['paging']['next'])

    def queue_paged_request(self, request_url):
        parsed_url = self.parse_request_url(request_url)
        request = {
            'id': str(parsed_url['id']),
            'request': str(parsed_url['request'])
        }
        if parsed_url['paging_token'] not in self.paging_tokens:
            self.queued_requests.append(request)
        self.paging_tokens.append(parsed_url['paging_token'])

    def parse_request_url(self, request_url):
        parsed = urlparse.urlparse(request_url)
        queries = urlparse.parse_qs(parsed.query)
        path = parsed.path[1:]
        path_elements = path.split('/')
        paging_token = ''
        if '__paging_token' in queries:
            paging_token = queries['__paging_token']
        return {
            'id': path_elements[0],
            'request': path,
            'paging_token': paging_token
        }

    def batch_to_request_url(self, batch):
        request_string = '?batch=['
        for request in batch:
            if request_string is not '?batch=[':
                request_string += ','
            request_string += '{"method":"GET", "relative_url":"' + str(request['request']) + '?limit=500"}'
        request_string += ']'
        url = 'https://graph.facebook.com/' + \
              str(request_string) + \
              '&access_token=' + str(self.access_token) + \
              '&method=post'
        return url