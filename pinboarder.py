import requests
from xml.etree import ElementTree
import datetime
from secrets import pinboard_api_token

def time_of_last_update():
    r = requests.get('https://api.pinboard.in/v1/posts/update', params={'auth_token': pinboard_api_token})
    root = ElementTree.fromstring(r.text)
    timestring = root.attrib['time']
    time = datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ')
    return time

if __name__ == '__main__':
    print('Last Update:', time_of_last_update())
