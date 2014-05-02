import os
from Queue import Queue
import sys
from threading import Thread
import time
from TwitterAPI import TwitterAPI


twapi = TwitterAPI(os.environ.get('TW_CONSUMER_KEY'),
                   os.environ.get('TW_CONSUMER_SECRET'),
                   os.environ.get('TW_ACCESS_TOKEN'),
                   os.environ.get('TW_ACCESS_TOKEN_SECRET'))


def lookup_ids(handles):
    """ Fetch the twitter ids of each screen_name. """
    ids = set()
    for handle_list in [handles[100 * i:100 * i + 100] for i in range(len(handles))]:
        if len(handle_list) > 0:
            print handle_list
            r = twapi.request('users/lookup', {'screen_name': ','.join(handle_list)})
            for item in r.get_iterator():
                ids.add(item['id_str'])
    return ids


def tweets_for_id(user_id, limit=1e10):
    """ Collect the most recent 3200 tweets for this user_id, sleeping to deal with rate limits."""
    # Map id to screen_name
    r = twapi.request('users/lookup', {'user_id': user_id})
    if r.status_code == 200:  # something went wrong
        sname = [t for t in r][0]['screen_name']
        return tweets_for_user(sname, limit)
    else:
        sys.stderr.write('error:' % r.text)


def tweets_for_user(screen_name, limit=1e10):
    """ Collect the most recent 3200 tweets for this user, sleeping to deal with rate limits."""
    qu = Queue()
    p = Thread(target=_tweets_for_user, args=(qu, screen_name, limit))
    p.start()
    p.join(900)
    if p.is_alive():
        sys.stderr.write('no results after 15 minutes for %s. Aborting.' % screen_name)
        return []
    else:
        return qu.get()


def _tweets_for_user(qu, screen_name, limit=1e10):
    max_id = None
    tweets = []
    while True:
        # TODO: Have to kill threads after some time; otherwise, we make too many...
        try:
            if max_id:
                response = twapi.request('statuses/user_timeline', {'screen_name': screen_name, 'count': 200, 'max_id': max_id})
            else:
                response = twapi.request('statuses/user_timeline', {'screen_name': screen_name, 'count': 200})
            if response.status_code != 200:  # something went wrong
                sys.stderr.write('Error: %s\nSleeping for 5 minutes...\n' % response.text)
                time.sleep(300)
            else:
                items = [t for t in response]
                if len(items) == 0:
                    qu.put(tweets)
                    return
                else:
                    sys.stderr.write('fetched %d more tweets for %s\n' % (len(items), screen_name))
                    tweets.extend(items)
                    if len(tweets) >= limit:
                        qu.put(tweets[:limit])
                        return
                max_id = min(t['id'] for t in response) - 1
        except Exception as e:
            sys.stderr.write('Error: %s\nSleeping for 5 minutes...\n' % e)
            time.sleep(300)


def track_user_ids(ids):
    """ Return an iterator tweets from users in this id list. """
    results = twapi.request('statuses/filter', {'follow': ','.join(ids)})
    return results.get_iterator()
