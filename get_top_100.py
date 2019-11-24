import os
import pandas as pd

from scoring_model import prep_data,get_tokenizer
from nltk.translate.bleu_score import sentence_bleu
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences

def clean_gen_tweets(filename,delimiter='===================='):
    with open(filename) as f:
        gen_tweets=[line.strip() for line in f]
        gen_tweets=''.join(gen_tweets).split(delimiter)

    gen_tweets=[tweet.replace('<|startoftext|>','') for tweet in gen_tweets]
    gen_tweets=[tweet.replace('<|endoftext|>','') for tweet in gen_tweets]

    return gen_tweets

def predict_scores(m,gen_tweets):
    sas=prep_data()
    max_tweet_len=sas['tweet_len'].max()
    tokenizer=get_tokenizer(sas,vocab_size=20000)
    sequences=tokenizer.texts_to_sequences(gen_tweets)
    X_new=pad_sequences(sequences,maxlen=max_tweet_len)

    return m.predict(X_new).ravel()

def add_bleu(top100):
    # takes forever to run
    # ignoring for now
    reference=[tweet.split() for tweet in pd.read_csv('data/stephenasmith_sa.csv.gz')['full_text']]
    top100['bleu']=[sentence_bleu(reference,tweet.split()) for tweet in top100['tweet']]
    return top100

def main():
    m=load_model('saved_models/scoring_model.h5')
    gpt_files=sorted(f for f in os.listdir('gpt-2_output') if f.startswith('gpt'))
    for file in gpt_files:
        gen_tweets=clean_gen_tweets('gpt-2_output/'+file)
        scores=predict_scores(m,gen_tweets)
        top100=pd.DataFrame({'tweet':gen_tweets,'score':scores}).sort_values('score',ascending=False)
        top100=top100.iloc[:100].reset_index(drop=True)
        with open('gpt-2_output/top100_'+file,'w') as f:
            for tweet,score in zip(top100['tweet'],top100['score']):
                f.write('score: '+str(score)+'\n')
                f.write(tweet+'\n')
                f.write('\n')
        print('saved:','gpt-2_output/top100_'+file)

if __name__=='__main__':
    main()
