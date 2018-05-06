# PinBoarder

Prettyfies Youtube links on Pinboard.

I have a somewhat complicated relationship with Youtube. In particular, their read-later system just doesn't work for me. Instead, I subscribe to my favorite channels in my RSS reader, and use [Pinboard](https://pinboard.in/) as my read-later system.

This works beautifully, except every RSS reader seems to have a different idea about how to format that Pinboard entry, and most of them do not include the video length or the channel name. But as luck would have it, Pinboard has an API, so this problem is fixeable!

PinBoarder downloads all your bookmarks from Pinboard, and fixes up every Youtube link to

> ### {{TITLE}} ({{duration}})
> by {{channel}} on {{publish-date}}

and tags it as "youtube".

You need to save your [Youtube API token](https://developers.google.com/youtube/v3/getting-started) and your [Pinboard API token](https://pinboard.in/settings/password) in a separate file `secrets.py` like this:

```python
pinboard_api_token = 'foobar:ABCDEFGHIJKLMNOPQRSTUVW'
youtube_api_token = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
```

Then put this script in a cron job (at most every three minutes), and enjoy.
