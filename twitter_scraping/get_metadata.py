# some code forked from https://github.com/bpb27/twitter_scraping

import argparse
import csv
import json
import math
import os
import tweepy
from time import sleep

def is_retweet(entry):
    return 'retweeted_status' in entry.keys()

def get_source(entry):
    if '<' in entry['source']:
        return entry['source'].split('>')[1].split('<')[0]
    else:
        return entry['source']

def arg_parser():
    parser=argparse.ArgumentParser(description='scraping twitter data')
    parser.add_argument('-u','--user',help='username of account to scrape')

    return parser

def main():
    args=arg_parser().parse_args()
    user=args.user.lower()
    id_dir='ids/{}/'.format(user)

    if not os.path.isdir('meta/'):
        os.mkdir('meta/')

    if not os.path.isdir('meta/'+user+'/'):
        os.mkdir('meta/{}/'.format(user))

    # Twitter API stuff
    with open('api_keys.json') as f:
        keys=json.load(f)
    auth=tweepy.OAuthHandler(keys['consumer_key'],keys['consumer_secret'])
    auth.set_access_token(keys['access_token'],keys['access_token_secret'])
    api=tweepy.API(auth)

    id_files=sorted(f for f in os.listdir(id_dir) if f.startswith('ids_'))
    for id_file in id_files:
        print('scraping:',id_file)
        with open(id_dir+id_file) as f:
            ids=json.load(f)
        output_file='meta/{}/tweets_{}.csv'.format(user,id_file[4:-5])
        tweet_data=[]
        start=0
        end=100
        limit=len(ids)
        i=math.ceil(limit/100)

        for go in range(i):
            print('currently getting {} - {}'.format(start,end))
            sleep(6)  # needed to prevent hitting API rate limit
            id_batch=ids[start:end]
            start+=100
            end+=100
            tweets=api.statuses_lookup(id_batch,tweet_mode='extended')
            for tweet in tweets:
                entry=dict(tweet._json)
                t={'created_at':entry['created_at'],
                   'full_text': entry['full_text'],
                   'in_reply_to_screen_name':entry['in_reply_to_screen_name'],
                   'retweet_count':entry['retweet_count'],
                   'favorite_count':entry['favorite_count'],
                   'source':get_source(entry),
                   'id_str':entry['id_str'],
                   'is_retweet': is_retweet(entry)}
                tweet_data.append(t)

        fields=['favorite_count','source','full_text','in_reply_to_screen_name','is_retweet','created_at','retweet_count','id_str']
        with open(output_file,'w') as f:
            writer=csv.writer(f)
            writer.writerow(fields)
            for x in tweet_data:
                writer.writerow([x['favorite_count'],x['source'],x['full_text'],x['in_reply_to_screen_name'],x['is_retweet'],x['created_at'],x['retweet_count'],x['id_str']])
        print('saved:',output_file)

if __name__=='__main__':
    main()
