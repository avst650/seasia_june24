# !python -m pip install pandas
# !python -m pip install pysentimiento
# !python -m pip install accelerate=0.20.3

import requests, pandas as pd
from pysentimiento import create_analyzer
from pysentimiento.preprocessing import preprocess_tweet

n=100
c=1
df=pd.DataFrame(columns=['reddit_comments', 'pre_process_data'])
analyzer = create_analyzer(task="sentiment", lang="en")

for i in range(n):
    try:
        url='https://api.pullpush.io/reddit/search/comment/?q=toyota&before=1680303707'
        if c>1:
            url=f'https://api.pullpush.io/reddit/search/comment/?q=toyota&before={bef}'
            
        resp=requests.get(url)
        data=resp.json()
        bef=data['data'][-1]['created_utc']
        comments=[]
        pos = []
        neu=[]
        neg =[]
    
        for dic in data['data']:
            comm=dic['body']
            comments.append(dic['body'])
        
        dt=pd.DataFrame(comments, columns=['reddit_comments'])
        dt['pre_process_data'] = dt['reddit_comments'].apply(lambda x : preprocess_tweet(x))
        # dt['label']= dt['pre_process_data'].apply(lambda x :analyzer.predict(x).output)
        
        for i in dt['pre_process_data']:
            dc = analyzer.predict(i).probas
            pos.append(dc['POS'])
            neu.append(dc['NEU'])
            neg.append(dc['NEG'])

        dt['POS'], dt['NEU'], dt['NEG']= pos, neu, neg

        df=pd.concat([df, dt])
        df.drop(['pre_process_data'],axis =1, inplace =True)
        df.reset_index(drop="index", inplace=True)
        # print('df: ', len(df))
        # df.to_csv('new.csv', index=False)
        c+=1

    except Exception as e:
        print(e)

df.to_csv('final.csv', index=False)
print('CSV saved!')