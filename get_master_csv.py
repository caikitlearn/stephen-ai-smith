import argparse
import os
import numpy as np
import pandas as pd

def arg_parser():
    parser=argparse.ArgumentParser(description='scraping twitter ids')
    parser.add_argument('-u','--user',help='username of account to scrape')
    return(parser)

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

def main():
    args=arg_parser().parse_args()
    user=args.user.lower()

    master_csv=compile_master(user)
    master_csv['std_favorite_count']=get_std_count(master_csv,'favorite_count')
    master_csv['std_retweet_count']=get_std_count(master_csv,'retweet_count')

    if not os.path.isdir('data/'):
        os.mkdir('data/')

    master_csv.to_csv('data/{}.csv.gz'.format(user),compression='gzip')

if __name__=='__main__':
    main()
