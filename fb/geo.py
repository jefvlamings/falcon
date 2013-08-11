import requests
from math import radians, cos, sin, asin, sqrt


def distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """

    if lon1 is None or lat1 is None or lon2 is None or lat2 is None:
        return None

    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


class Mapquest:

    SECRET_KEY = 'Fmjtd%7Cluub25u72q%2Ca2%3Do5-9u8xl6'

    def request(self, request):
        url = 'http://open.mapquestapi.com/geocoding/v1/batch' \
              '?key=' + self.SECRET_KEY + \
              '&' + request
        response = requests.get(url).json()
        try:
            status_code = response['info']['statuscode']
            if status_code is not 0:
                raise Exception('MapQuest status: ' + self.status_message(status_code))
                return None
        except IndexError:
            return None
        return response['results']

    def batch_request_names(self, names=[]):
        response = []
        while len(names) > 0:
            names_bit = names[0:99]
            response += self.batch_request_names_bit(names_bit)
            names = names[99:]
        return response

    def batch_request_names_bit(self, names):
        request_string = ''
        for name in names:
            if request_string is not '':
                request_string += '&'
            request_string += 'location=' + name

        response = self.request(request_string)
        return response

    def status_message(self, code):
        messages = {
            0: 'A successful geocode call.',
            400: 'Error with input - The error message will start with: "Illegal argument from request:" '
                 'followed by the specific error condition.',
            403: 'Key related error - The error message will attempt to explain why there was an error with the '
                 'key and should provide a link to the Developer Network.',
            500: 'Unknown error - The error message will start with: "Error processing request:" followed by the '
                 'message from the exception.',
            606: 'Exceeded maximum number of locations. (Max=100, Actual=149)'
        }
        return messages[code]