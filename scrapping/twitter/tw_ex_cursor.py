import tweepy
from tweepy import OAuth1UserHandler, API
import pandas as pd
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

try:
    auth = OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
    api = API(auth)

    keyw=input('enter keyword: ')
    query = f"{keyw} -filter:retweets"
    # tweets = api.search_tweets(KEYWORDS, lang="en", count=100, tweet_mode="extended")
    limit=5

    tweets = tweepy.Cursor(api.search_tweets, q=query, count=100, tweet_mode='extended').items(limit)
    columns = ['User', 'Tweet_link']
    data = []
    for tweet in tweets:
        data.append([tweet.user.screen_name, f'https://twitter.com/twitter/status/{tweet.id}'])
        
    df = pd.DataFrame(data, columns=columns)
    df.to_excel(f'{keyw}.xlsx',sheet_name='Sheet1', startrow=0, startcol=0, header=True, index=False)
    
except Exception as e:
    print(e)
