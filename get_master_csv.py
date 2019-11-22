import argparse
import csv
import numpy as np
import os
import pandas as pd
import string
import re

from bs4 import BeautifulSoup
from emoji import UNICODE_EMOJI

def arg_parser():
    parser=argparse.ArgumentParser(description='scraping twitter ids')
    parser.add_argument('-u','--user',help='username of account to scrape')

    return parser

def compile_master(user):
    meta_dir='twitter_scraping/meta/{}/'.format(user)
    csv_files=sorted(f for f in os.listdir(meta_dir) if f.startswith('tweets_'))

    master_csv=pd.DataFrame()
    for csv_file in csv_files:
        master_csv=pd.concat([master_csv,pd.read_csv(meta_dir+csv_file)],axis=0)

    master_csv['created_at']=pd.to_datetime(master_csv['created_at'])
    master_csv.sort_values('created_at',inplace=True)
    master_csv.reset_index(drop=True,inplace=True)
    master_csv['created_year']=master_csv['created_at'].dt.year

    return master_csv

def get_std_count(master_csv,col):
    annual_means={}
    annual_stds={}

    for year in master_csv['created_year'].unique():
        n_fav=master_csv.loc[master_csv['created_year']==year,col].values
        annual_means[year]=np.mean(n_fav)
        annual_stds[year]=np.std(n_fav)

    return [(c-annual_means[year])/annual_stds[year] for c,year in zip(master_csv[col],master_csv['created_year'])]

def remove_html(tweet):
    # replacing URLs with the urlurlurl token
    # can't use <url> as the token or it will get removed by BeautifulSoup
    cleaned_tweet=re.sub(r'(?i)http\S+','urlurlurl',tweet)
    cleaned_tweet=re.sub(r'(?i)\S+.com','urlurlurl',cleaned_tweet)

    # remove HTML elements from the tweet
    cleaned_tweet=BeautifulSoup(cleaned_tweet,'lxml').get_text()

    return cleaned_tweet

def clean_tweet_gpt2(tweet):
    # for GPT-2, we can keep punctuation
    # just need to remove HTML and replace @ wth <at>
    cleaned_tweet=remove_html(tweet)

    # replace urlurlurl with aesthetically pleasing <url> token
    cleaned_tweet=cleaned_tweet.replace('urlurlurl','<url>')
    # replace @ with <at> to avoid spamming random people
    cleaned_tweet=cleaned_tweet.replace('@','<at>')

    return cleaned_tweet

def clean_tweet(tweet):
    # for the sentiment analysis portion, remove punctuation as well
    cleaned_tweet=remove_html(tweet)

    # remove punctuation except @ and # (sadly this means no smileys)
    # also handle apostrophes separately
    punctuation_to_remove=''.join(p for p in string.punctuation if p not in ['@','#',"'"])
    cleaned_tweet=cleaned_tweet.translate(str.maketrans(punctuation_to_remove,' '*len(punctuation_to_remove)))

    # remove special characters
    char_map={"'":'','\u201c':'','\u201d':'','\u2018':'','\u2019':'',
              '\u200d':' ','\u2026':' '}
    for char in char_map.keys():
        cleaned_tweet=cleaned_tweet.replace(char,char_map[char])

    # replace urlurlurl with aesthetically pleasing <url> token
    # replace @ with <at> so bot does not spam random people
    cleaned_tweet=cleaned_tweet.replace('urlurlurl','<url>')
    cleaned_tweet=cleaned_tweet.replace('@','<at>')

    # padding emojis so they show up as their own token
    emojis=[char for char in tweet if char in UNICODE_EMOJI]
    if len(emojis)>0:
        for emoji in emojis:
            cleaned_tweet=cleaned_tweet.replace(emoji,' {} '.format(emoji))

    return cleaned_tweet

def main():
    args=arg_parser().parse_args()
    user=args.user.lower()

    if not os.path.isdir('data/'):
        os.mkdir('data/')

    # master csv
    master_csv=compile_master(user)
    master_csv['std_favorite_count']=get_std_count(master_csv,'favorite_count')
    master_csv['std_retweet_count']=get_std_count(master_csv,'retweet_count')
    master_csv.to_csv('data/{}.csv.gz'.format(user),index=False,compression='gzip')
    print('saved master csv:','data/{}.csv.gz'.format(user))

    # csv fpr GPT-2
    with open('data/{}_gpt2.csv'.format(user),'w') as f:
        writer=csv.writer(f,quoting=csv.QUOTE_ALL)
        for tweet in master_csv['full_text']:
            writer.writerow([clean_tweet_gpt2(tweet)])
    print('saved training data for GPT-2:','data/{}_gpt2.csv'.format(user))

    # csv for sentiment analysis
    master_csv['full_text']=[clean_tweet(tweet) for tweet in master_csv['full_text']]
    master_csv.to_csv('data/{}_sa.csv.gz'.format(user),index=False,compression='gzip')
    print('saved data for sentiment analysis:','data/{}_sa.csv.gz'.format(user))

if __name__=='__main__':
    main()
