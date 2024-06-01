import tweepy
from tweepy import OAuth1UserHandler, API
import pandas as pd
import configparser

# config = configparser.ConfigParser()
# config.read('config.ini')

# api_key = config['twitter']['api_key']
# api_key_secret = config['twitter']['api_key_secret']
# access_token = config['twitter']['access_token']
# access_token_secret = config['twitter']['access_token_secret']
bearer_token="AAAAAAAAAAAAAAAAAAAAAOYzsAEAAAAAbc0zvRRU5v6owuo8mGMKn1JnsGs%3DRZxzL0L9u888n3KbulGoR2oKhDsbJBKqO6Utg9qEiDBKmMyj0f"

client = tweepy.Client(bearer_token)

keyw=input('Enter keyword you want to search: ')
how_many=int(input('How many tweets do you want: '))

query = f'{keyw} -is:retweet lang:en'
all_tweets = []

# auth = OAuth1UserHandler(api_key, api_key_secret, access_token, access_token_secret)
# api = API(auth)

tweets = tweepy.Paginator(client.search_recent_tweets,
                          query=query,
                          expansions=['author_id'],
                          user_fields=['id', 'name', 'username','entities','created_at'],
                          tweet_fields=['created_at'],
                          max_results=100).flatten(limit=how_many)

a=[]
u=[]
t=[]
tx=[]
ti=[]
for tweet in tweets:
    a.append(tweet.author_id)
    t.append(f'https://twitter.com/twitter/status/{tweet.id}')
    tx.append(tweet.text)
    ti.append((tweet.created_at).strftime('%d/%m/%Y-%H:%M:%S'))

x=0
y=100
l=len(a)
loo=l/100
for i in range(int(loo)+1):
    try:
        b=a[x:y]
        response = client.get_users(ids=b)
        for user in response.data:
            u.append(f'https://twitter.com/{user.username}')
        x+=100
        y+=100
    except Exception as e:
        # print(e)
        break

df = pd.DataFrame(zip(u, ti, t, tx), columns=['User_Handle', 'Date', 'Tweet_Link', 'Tweet_Text'])
df.to_excel(f'{keyw}.xlsx',sheet_name='Sheet1', startrow=0, startcol=0, header=True, index=False)
print('All tweets saved :)')

# print(len(u))
# se=set(u)
# lse=list(se)
# print(len(lse))
