import os
from Queue import Queue
import sys
from threading import Thread
import time
import twitter

twapi = twitter.Twitter(auth=twitter.OAuth(os.environ.get('TW_ACCESS_TOKEN'),
                                           os.environ.get('TW_ACCESS_TOKEN_SECRET'),
                                           os.environ.get('TW_CONSUMER_KEY'),
                                           os.environ.get('TW_CONSUMER_SECRET')))

twstream = twitter.TwitterStream(auth=twitter.OAuth(os.environ.get('TW_ACCESS_TOKEN'),
                                                    os.environ.get('TW_ACCESS_TOKEN_SECRET'),
                                                    os.environ.get('TW_CONSUMER_KEY'),
                                                    os.environ.get('TW_CONSUMER_SECRET')))


def tweets_for_user(screen_name, limit=1e10):
    qu = Queue()
    p = Thread(target=_tweets_for_user, args=(qu, screen_name, limit))
    p.start()
    p.join(900)
    if p.is_alive():
        sys.stderr.write('no results after 15 minutes for', screen_name, '. Aborting.')
        return None
    else:
        return qu.get()


def _tweets_for_user(qu, screen_name, limit=1e10):
    max_id = None
    tweets = []
    while True:
        try:
            if max_id:
                response = twapi.statuses.user_timeline(screen_name=screen_name, count=200, max_id=max_id)
            else:
                response = twapi.statuses.user_timeline(screen_name=screen_name, count=200)
            if len(response) == 0:
                qu.put(tweets)
                return
            else:
                sys.stderr.write('fetched %d more tweets for %s\n' % (len(response), screen_name))
                tweets.extend(response)
                if len(tweets) >= limit:
                    qu.put(tweets[:limit])
                    return
                # print json.dumps(response)
                max_id = min(t['id'] for t in response) - 1
        except Exception as e:
            if '404' in str(e.e):
                sys.stderr.write('Error: %s\nSkipping...\n' % e)
                qu.put(None)
                return
            else:
                sys.stderr.write('Error: %s\nSleeping for 5 minutes...\n' % e)
                time.sleep(300)
