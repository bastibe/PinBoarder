#!/usr/bin/env python3.6
import requests
from xml.etree import ElementTree
import datetime
import re
import urllib.parse
import time
import sys
import pathlib
from secrets import pinboard_api_token, youtube_api_token


def fix_windows():
     import codecs
     sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def time_of_last_change():
    r = requests.get('https://api.pinboard.in/v1/posts/update', params={'auth_token': pinboard_api_token})
    root = ElementTree.fromstring(r.text)
    timestring = root.attrib['time']
    return timestring

def get_recent_bookmarks(count=15):
    r = requests.get('https://api.pinboard.in/v1/posts/recent',
                     params={'auth_token': pinboard_api_token, 'count': count})
    root = ElementTree.fromstring(r.text)
    bookmarks = [post.attrib for post in root]
    return bookmarks

def get_all_bookmarks():
    r = requests.get('https://api.pinboard.in/v1/posts/all',
                     params={'auth_token': pinboard_api_token, 'meta': 'no'})
    root = ElementTree.fromstring(r.text)
    bookmarks = [post.attrib for post in root]
    return bookmarks

def fix_youtube_bookmark(href, time, description, extended, tag, hash, toread='no', shared='no', meta=None):
    # update tags:
    if not tag:
        tag = 'youtube'
    elif 'youtube' not in tag:
        tag += ' youtube'

    # get video metadata from google:
    if 'youtube.com' in href:
        video_id = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)['v'][0]
    elif 'youtu.be' in href:
        video_id = urllib.parse.urlparse(href).path[1:]
    r = requests.get('https://www.googleapis.com/youtube/v3/videos',
                     params={'key': youtube_api_token,
                             'id': video_id,
                             'part': 'contentDetails,snippet'})
    data = r.json()

    if not data['items']:
         return dict(href=href, time=time, description=description,
                     extended=extended, tag=tag, hash=hash,
                     shared=shared, toread=toread)

    # extract metadata:
    title = data['items'][0]['snippet']['title']
    channel_name = data['items'][0]['snippet']['channelTitle']
    publishedstring = data['items'][0]['snippet']['publishedAt']
    published = datetime.datetime.strptime(publishedstring, '%Y-%m-%dT%H:%M:%SZ')
    durationstring = data['items'][0]['contentDetails']['duration']
    m = re.match('PT(?P<h>[0-9]+H)?(?P<m>[0-9]+M)?(?P<s>[0-9]+S)?', durationstring)
    duration = datetime.time(hour=0 if not m.group('h') else int(m.group('h').strip('H')),
                             minute=0 if not m.group('m') else int(m.group('m').strip('M')),
                             second=0 if not m.group('s') else int(m.group('s').strip('S')))
    description = f'{title} ({duration})'
    extended = f'by {channel_name} on {published}'
    return dict(href=href, time=time, description=description, extended=extended, tag=tag, hash=hash, shared=shared, toread=toread)


def add_bookmark(href, time, description, extended, tag, hash, replace, toread='no', shared='no'):
    r = requests.get('https://api.pinboard.in/v1/posts/add',
                     params={'auth_token': pinboard_api_token,
                             'url': href,
                             'dt': time,
                             'description': description,
                             'extended': extended,
                             'tags': tag,
                             'toread': toread,
                             'shared': shared,
                             'replace': replace})
    if 'done' in r.text:
        return
    else:
        raise(RuntimeError(r.text))


if __name__ == '__main__':
    if sys.platform == 'win32':
         fix_windows()

    last_change = time_of_last_change()
    changefile = pathlib.Path('lastchange')
    if changefile.exists():
        with changefile.open() as f:
            if f.read() == last_change:
                sys.exit(0)

    for bookmark in get_all_bookmarks():
        try:
            if (('youtube.com' in bookmark['href'] or 'youtu.be' in bookmark['href']) and
                'youtube' not in bookmark['tag'] and 'playlist' not in bookmark['href'] and
                'channel' not in bookmark['href']):
                add_bookmark(replace='yes', **fix_youtube_bookmark(**bookmark))
                time.sleep(4)
        except Exception as err:
             print('could not parse {}'.format(bookmark['href']), 'because', err)

    with changefile.open('w') as f:
         f.write(last_change)
