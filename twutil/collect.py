import json
import os
import sys
from threading import Thread
import time
import traceback
from TwitterAPI import TwitterAPI

try:
    from Queue import Queue
except:
    from queue import Queue

twapi = None


def reinit():
    global twapi
    twapi = TwitterAPI(os.environ.get('TW_CONSUMER_KEY'),
                       os.environ.get('TW_CONSUMER_SECRET'),
                       os.environ.get('TW_ACCESS_TOKEN'),
                       os.environ.get('TW_ACCESS_TOKEN_SECRET'))

reinit()


def list_members(slug, owner_screen_name, limit=1e10):
    """See https://dev.twitter.com/rest/reference/get/lists/members"""
    cursor = -1
    members = []
    try:
        response = twapi.request('lists/members', {'slug': slug, 'owner_screen_name': owner_screen_name, 'cursor': cursor, 'count': 5000})
        if response.status_code in [88, 130, 420, 429]:  # rate limit
            sys.stderr.write('Error for %s/%s: %s\nSleeping for 5 minutes...\n' % (owner_screen_name, slug, response.text))
            time.sleep(301)
        elif response.status_code != 200:
            sys.stderr.write('Skipping bad query: %s\n' % response.text)
            return members
        else:
            items = [r['screen_name'] for r in response if 'screen_name' in r]
            return items
    except Exception as e:
        sys.stderr.write('Error: %s\nskipping...\n' % e)
        return members
    return members


def lookup_handles(ids):
    """ Fetch the twitter screen_names of each id. """
    names = set()
    for id_list in [ids[100 * i:100 * i + 100] for i in range(len(ids))]:
        if len(id_list) > 0:
            while True:
                r = twapi.request('users/lookup', {'user_id': ','.join([str(i) for i in id_list])})
                if r.status_code in [88, 130, 420, 429]:  # rate limit
                    sys.stderr.write('Sleeping off rate limit for %s: %s\n' % (str(id_list), r.text))
                    time.sleep(301)
                elif r.status_code == 200:
                    for item in r.get_iterator():
                        names.add((item['screen_name'], item['id_str']))
                    break
                else:
                    sys.stderr.write('Error: %s\nSkipping %s...\n' % (str(id_list), r.text))
                    break

    return names


def lookup_ids(handles):
    """ Fetch the twitter ids of each screen_name. """
    ids = set()
    for handle_list in [handles[100 * i:100 * i + 100] for i in range(len(handles))]:
        if len(handle_list) > 0:
            while True:
                r = twapi.request('users/lookup', {'screen_name': ','.join(handle_list)})
                if r.status_code in [88, 130, 420, 429]:  # rate limit
                    sys.stderr.write('Sleeping off rate limit for %s: %s\n' % (str(handle_list), r.text))
                    time.sleep(300)
                elif r.status_code == 200:
                    for item in r.get_iterator():
                        ids.add(item['id_str'])
                    break
                else:
                    sys.stderr.write('Error: %s\nSkipping %s...\n' % (str(handle_list), r.text))
                    break

    return ids


def tweets_for_id(user_id, limit=1e10):
    """ Collect the most recent 3200 tweets for this user_id, sleeping to deal with rate limits."""
    # Map id to screen_name
    r = twapi.request('users/lookup', {'user_id': user_id})
    if r.status_code == 200:
        sname = [t for t in r][0]['screen_name']
        return tweets_for_user(sname, limit)
    else:
        sys.stderr.write('error:' % r.text)


def tweets_for_user(screen_name, limit=1e10):
    """ Collect the most recent 3200 tweets for this user, sleeping to deal with rate limits."""
    qu = Queue()
    p = Thread(target=_tweets_for_user, args=(qu, screen_name, limit))
    p.start()
    p.join(910)
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
            if response.status_code == 34 or response.status_code == 404 or response.status_code == 401:
                sys.stderr.write('Skipping bad user: %s\n' % response.text)
                qu.put(tweets)
                return
            elif response.status_code != 200:  # something went wrong
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
            sys.stderr.write('Error: %s Skipping...\n' % e)


def track_user_ids(ids):
    """ Return an iterator tweets from users in this id list. """
    results = twapi.request('statuses/filter', {'follow': ','.join(ids)})
    return results.get_iterator()


def friends_for_id(id_, limit=1e10):
    # FIXME: DRY from _tweets_for_user
    cursor = -1
    friends = []
    while len(friends) < limit:
        try:
            response = twapi.request('friends/ids', {'user_id': id_, 'count': 5000,
                                                     'cursor': cursor, 'stringify_ids': True})
            if response.status_code in [88, 130, 420, 429]:  # rate limit
                sys.stderr.write('Error for %s: %s\nSleeping for 5 minutes...\n' % (id_, response.text))
                time.sleep(300)
            elif response.status_code != 200:
                sys.stderr.write('Skipping bad user: %s\n' % response.text)
                return friends
            else:
                result = [r for r in response][0]
                items = result['ids']
                if len(items) == 0:
                    return friends
                else:
                    sys.stderr.write('fetched %d more friends for %s\n' % (len(items), id_))
                    time.sleep(1)
                    friends.extend(items)
                    if len(friends) >= limit:
                        return friends[:limit]
                cursor = result['next_cursor']
        except Exception as e:
            sys.stderr.write('Error: %s\nskipping...\n' % e)
            return friends
    return friends


def friends_for_user(screen_name, limit=5000):
    id_ = [i for i in lookup_ids([screen_name])]
    if len(id_) == 1:
        return friends_for_id(id_, limit)
    else:
        sys.stderr.write('cannot find id for user %s' % screen_name)
        return []


def followers_for_user(screen_name, limit=1e10):
    id_ = [i for i in lookup_ids([screen_name])]
    if len(id_) == 1:
        return followers_for_id(id_, limit)
    else:
        sys.stderr.write('cannot find id for user %s' % screen_name)
        return []


def get_followers(id_=None, screen_name=None, limit=1e10):
    """ Either id_ or screen_name must not be None. """
    # FIXME: DRY from _tweets_for_user
    if not (id_ or screen_name):
        raise Exception("either id_ or screen_name must not be None")
    if id_:
        key = 'user_id'
        val = id_
    else:
        key = 'screen_name'
        val = screen_name
    cursor = -1
    followers = []
    while len(followers) < limit:
        try:
            response = twapi.request('followers/ids', {key: val, 'count': 5000,
                                                       'cursor': cursor, 'stringify_ids': True})
            if response.status_code in [88, 130, 420, 429]:  # rate limit
                sys.stderr.write('Error for %s: %s\nSleeping for 5 minutes...\n' % (val, response.text))
                time.sleep(300)
            elif response.status_code != 200:
                sys.stderr.write('Skipping bad user: %s\n' % response.text)
                return followers
            else:
                result = json.loads(response.text)
                items = [r for r in response]
                if len(items) == 0:
                    return followers
                else:
                    sys.stderr.write('fetched %d more followers for %s\n' % (len(items), val))
                    time.sleep(1)
                    followers.extend(items)
                    if len(followers) >= limit:
                        return followers[:limit]
                cursor = result['next_cursor']
        except Exception as e:
            sys.stderr.write('Error: %s\nskipping...\n' % e)
            sys.stderr.write(traceback.format_exc())
            return followers
    return followers


def followers_for_id(id_, limit=1e10):
    return get_followers(id_=id_, limit=limit)


def followers_for_screen_name(screen_name, limit=1e10):
    return get_followers(screen_name=screen_name, limit=limit)
