# some code forked from https://github.com/bpb27/twitter_scraping

import argparse
import datetime
import json
import os
import pandas as pd

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from time import sleep

def arg_parser():
    parser=argparse.ArgumentParser(description='scraping twitter ids')
    parser.add_argument('-u','--user',help='username of account to scrape')
    parser.add_argument('-y','--year',default=str(datetime.datetime.today().year),help='year for data collection')

    return parser

def main(delay=1,driver=webdriver.Safari(),id_selector='.time a.tweet-timestamp',tweet_selector='li.js-stream-item'):
    args=arg_parser().parse_args()
    user=args.user.lower()
    year=args.year

    if not os.path.isdir('ids/'):
        os.mkdir('ids/')

    if not os.path.isdir('ids/'+user+'/'):
        os.mkdir('ids/'+user+'/')

    twitter_ids_filename='ids/{}/ids_{}_{}.json'.format(user,user,year)
    date_range=[d.strftime('%F') for d in pd.date_range(year+'-01-01',str(int(year)+1)+'-01-01')]

    ids=[]
    for i in range(len(date_range)-1):
        url='https://twitter.com/search?f=tweets&vertical=default&q=from%3A'+user+'%20since%3A'+date_range[i]+'%20until%3A'+date_range[i+1]+'include%3Aretweets&src=typd'
        print('date:',date_range[i])
        driver.get(url)
        sleep(delay)

        try:
            found_tweets=driver.find_elements_by_css_selector(tweet_selector)
            increment=10

            while len(found_tweets)>=increment:
                # print('scrolling down to load more tweets')
                driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
                sleep(delay)
                found_tweets=driver.find_elements_by_css_selector(tweet_selector)
                increment+=10

            for tweet in found_tweets:
                try:
                    id=tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                    ids.append(id)
                except StaleElementReferenceException as e:
                    print('lost element reference',tweet)

        except NoSuchElementException:
            print('no tweets on this day')

        print('{} tweets found, {} total'.format(len(found_tweets),len(ids)))

    with open(twitter_ids_filename,'w') as outfile:
        json.dump(list(set(ids)),outfile)
        print('unique tweets found on this scrape:',len(ids))

    print('done')
    driver.close()

if __name__=='__main__':
    main()
