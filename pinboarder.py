import requests
from xml.etree import ElementTree
import datetime
import re
import urllib.parse
from secrets import pinboard_api_token, youtube_api_token


def fix_windows():
     import sys
     import codecs
     sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def time_of_last_change():
    r = requests.get('https://api.pinboard.in/v1/posts/update', params={'auth_token': pinboard_api_token})
    root = ElementTree.fromstring(r.text)
    timestring = root.attrib['time']
    time = datetime.datetime.strptime(timestring, '%Y-%m-%dT%H:%M:%SZ')
    return time

def get_recent_bookmarks(count=15):
    r = requests.get('https://api.pinboard.in/v1/posts/recent',
                     params={'auth_token': pinboard_api_token, 'count': count})
    root = ElementTree.fromstring(r.text)
    bookmarks = [post.attrib for post in root]
    return bookmarks

def fix_bookmark(href, time, description, extended, tag, hash, toread):
    if 'youtube.com' in href or 'youtu.be' in href:
        # update tags:
        if not tag:
            tag = 'youtube'
        elif 'youtube' not in tag:
            tag += ' youtube'
        # update description:
        r = requests.get('https://www.googleapis.com/youtube/v3/videos',
                         params={'key': youtube_api_token,
                                 'id': urllib.parse.parse_qs(urllib.parse.urlparse(href).query)['v'][0],
                                 'part': 'contentDetails,snippet'})
        data = r.json()
        title = data['items'][0]['snippet']['title']
        channel_name = data['items'][0]['snippet']['channelTitle']
        publishedstring = data['items'][0]['snippet']['publishedAt']
        published = datetime.datetime.strptime(publishedstring, '%Y-%m-%dT%H:%M:%S.%fZ')
        durationstring = data['items'][0]['contentDetails']['duration']
        m = re.match('PT(?P<h>[0-9]+H)?(?P<m>[0-9]+M)?(?P<s>[0-9]+S)', durationstring)
        duration = datetime.time(hour=0 if not m.group('h') else int(m.group('h').strip('H')),
                                 minute=0 if not m.group('m') else int(m.group('m').strip('M')),
                                 second=0 if not m.group('s') else int(m.group('s').strip('S')))
        description = f'{title} ({duration})'
        extended = f'by {channel_name} on {published}'
    return dict(href=href, time=time, description=description, extended=extended, tag=tag, hash=hash, toread=toread)


if __name__ == '__main__':
    fix_windows()
    # print('Last Update:', time_of_last_change())
    # bookmarks = get_recent_bookmarks()
    # print(bookmarks)
    bookmark = {'href': 'https://www.youtube.com/watch?v=9mPBmUR30-s', 'time': '2018-05-05T18:07:13Z', 'description': 'Good Game Design - God of War (PS4) - YouTube', 'extended': '', 'tag': '', 'hash': '66aabe3904ea7ae583939604fb09a190', 'toread': 'yes'}
    print(fix_bookmark(**bookmark))
