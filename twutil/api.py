import os
import twitter

twapi = twitter.Twitter(auth=twitter.OAuth(os.environ.get('TW_ACCESS_TOKEN'),
                                           os.environ.get('TW_ACCESS_TOKEN_SECRET'),
                                           os.environ.get('TW_CONSUMER_KEY'),
                                           os.environ.get('TW_CONSUMER_SECRET')))

# def create_twitter(oauth_file):
#     with open(oauth_file, 'rb') as csvfile:
#         rdr = csv.DictReader(csvfile, delimiter=' ')
#         creds = [r for r in rdr][0]
#         return twitter.Twitter(auth=twitter.OAuth(creds['access_token'], creds['access_token_secret'],
#                                                   creds['consumer_key'], creds['consumer_secret']))
