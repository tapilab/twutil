import json


class Tweet(object):
    """
    >>> tweet = Tweet(json.loads(test_tweet))
    >>> tweet.js['user']['name']
    u'Ellen DeGeneres'
    """

    def __init__(self, js):
        self.js = js

    def __str__(self):
        return u'\t'.join([self.js['user']['screen_name'], self.js['created_at'], self.js['text']])


def jsons2tweets(jsons):
    """
    >>> tweets = [t for t in jsons2tweets([test_tweet, test_tweet])]
    >>> len(tweets)
    2
    >>> tweets[0].js['user']['name']
    u'Ellen DeGeneres'
    """
    for js in jsons:
        yield Tweet(json.loads(js))


class User(object):
    def __init__(self, jsons):
        self.tweets = [Tweet(t) for t in jsons]


test_tweet = r'''{"favorited": false, "contributors": null, "truncated": false, "text": "If only Bradley's arm was longer. Best photo ever. #oscars http://t.co/C9U5NOtGap", "possibly_sensitive": false, "in_reply_to_status_id": null, "user": {"follow_request_sent": false, "profile_use_background_image": true, "default_profile_image": false, "id": 15846407, "profile_background_image_url_https": "https://pbs.twimg.com/profile_background_images/446411201413541888/uY6CCUHT.png", "verified": true, "profile_text_color": "000000", "profile_image_url_https": "https://pbs.twimg.com/profile_images/421402074153091072/fL_dFiNk_normal.jpeg", "profile_sidebar_fill_color": "C4C6CC", "entities": {"url": {"urls": [{"url": "http://t.co/rJNCGU9GhH", "indices": [0, 22], "expanded_url": "http://www.ellentv.com", "display_url": "ellentv.com"}]}, "description": {"urls": []}}, "followers_count": 28192772, "profile_sidebar_border_color": "FFFFFF", "id_str": "15846407", "profile_background_color": "3ABEE3", "listed_count": 99361, "is_translation_enabled": true, "utc_offset": -25200, "statuses_count": 8635, "description": "Comedian, talk show host and ice road trucker. My tweets are real, and they\\u2019re spectacular.", "friends_count": 46462, "location": "California", "profile_link_color": "3ABEE3", "profile_image_url": "http://pbs.twimg.com/profile_images/421402074153091072/fL_dFiNk_normal.jpeg", "following": false, "geo_enabled": false, "profile_banner_url": "https://pbs.twimg.com/profile_banners/15846407/1395265968", "profile_background_image_url": "http://pbs.twimg.com/profile_background_images/446411201413541888/uY6CCUHT.png", "screen_name": "TheEllenShow", "lang": "en", "profile_background_tile": false, "favourites_count": 160, "name": "Ellen DeGeneres", "notifications": false, "url": "http://t.co/rJNCGU9GhH", "created_at": "Thu Aug 14 03:50:42 +0000 2008", "contributors_enabled": false, "time_zone": "Pacific Time (US & Canada)", "protected": false, "default_profile": false, "is_translator": false}, "geo": null, "id": 440322224407314432, "favorite_count": 1998872, "lang": "en", "entities": {"symbols": [], "user_mentions": [], "hashtags": [{"indices": [51, 58], "text": "oscars"}], "urls": [], "media": [{"expanded_url": "http://twitter.com/TheEllenShow/status/440322224407314432/photo/1", "display_url": "pic.twitter.com/C9U5NOtGap", "url": "http://t.co/C9U5NOtGap", "media_url_https": "https://pbs.twimg.com/media/BhxWutnCEAAtEQ6.jpg", "id_str": "440322224092745728", "sizes": {"small": {"h": 191, "resize": "fit", "w": 340}, "large": {"h": 576, "resize": "fit", "w": 1024}, "medium": {"h": 338, "resize": "fit", "w": 600}, "thumb": {"h": 150, "resize": "crop", "w": 150}}, "indices": [59, 81], "type": "photo", "id": 440322224092745728, "media_url": "http://pbs.twimg.com/media/BhxWutnCEAAtEQ6.jpg"}]}, "created_at": "Mon Mar 03 03:06:13 +0000 2014", "retweeted": false, "coordinates": null, "in_reply_to_user_id_str": null, "in_reply_to_status_id_str": null, "in_reply_to_screen_name": null, "id_str": "440322224407314432", "place": null, "retweet_count": 3422680, "in_reply_to_user_id": null}'''















