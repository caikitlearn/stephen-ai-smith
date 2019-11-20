#  forked from https://github.com/bpb27/twitter_scraping

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from time import sleep

import argparse
import datetime
import json
import os
import pandas as pd

def arg_arser():
    parser=argparse.ArgumentParser(description='scraping twitter ids')
    parser.add_argument('-u','--user',help='username of account to scrape')
    parser.add_argument('-s','--start',help='date to start data collection in yyyy-mm-dd format')
    parser.add_argument('-e','--end',help='date to end data collection in yyyy-mm-dd format')
    return(parser)

def get_args():
    ap=argParser()
    args=ap.parse_args()
    return args

if __name__=='__main__':
    args=get_args()

    user=args.user.lower()
    start=args.start
    end=args.end

    delay=1  # time to wait on each page load before reading the page
    driver=webdriver.Safari()  # options are Chrome() Firefox() Safari()

    twitter_ids_filename='ids/ids_{}_to_{}.json'.format(start,end)
    date_range=[d.strftime('%F') for d in pd.date_range(start,end)]
    id_selector='.time a.tweet-timestamp'
    tweet_selector='li.js-stream-item'
    ids=[]

    for i in range(len(date_range)-1):
        url='https://twitter.com/search?f=tweets&vertical=default&q=from%3A'+\
            user+'%20since%3A'+start+'%20until%3A'+end+'include%3Aretweets&src=typd'
        print('username:',user)
        print('date:',date_range[i])
        driver.get(url)
        sleep(delay)

        try:
            found_tweets=driver.find_elements_by_css_selector(tweet_selector)
            increment=10

            while len(found_tweets)>=increment:
                print('scrolling down to load more tweets')
                driver.execute_script('window.scrollTo(0,document.body.scrollHeight);')
                sleep(delay)
                found_tweets=driver.find_elements_by_css_selector(tweet_selector)
                increment+=10

            print('{} tweets found, {} total'.format(len(found_tweets),len(ids)))

            for tweet in found_tweets:
                try:
                    id=tweet.find_element_by_css_selector(id_selector).get_attribute('href').split('/')[-1]
                    ids.append(id)
                except StaleElementReferenceException as e:
                    print('lost element reference',tweet)

        except NoSuchElementException:
            print('no tweets on this day')

    with open(twitter_ids_filename,'w') as outfile:
        json.dump(list(set(ids)),outfile)
        print('tweets found on this scrape: ',len(ids))

    print('all done here')
    driver.close()
