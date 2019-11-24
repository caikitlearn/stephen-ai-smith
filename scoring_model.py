import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.metrics import average_precision_score
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from tensorflow.keras.initializers import Constant
from tensorflow.keras.layers import Bidirectional,Dense,Dropout,Embedding,LSTM
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

def get_embedding_map(path):
    M={}
    with open(path) as f:
        for line in f:
            line_list=line.split()
            word=line_list[0]
            M[word]=np.array([float(val) for val in line_list[1:]])
    return M

def prep_data():
    sas=pd.read_csv('data/stephenasmith_sa.csv.gz',compression='gzip')
    sas['tweet_len']=[len(tweet.split()) for tweet in sas['full_text']]
    sas=sas.loc[sas['tweet_len']>=5].reset_index(drop=True)
    sas['log10_favorite_count']=np.log10(sas['favorite_count']+1)
    sas['is_good_tweet']=1*(sas['favorite_count']>=100)

    return sas

def get_tokenizer(sas,vocab_size):
    tokenizer=Tokenizer(num_words=vocab_size,
                        filters='!"$%&()*+,-./:;=?[\\]^_`{|}~\t\n',
                        oov_token='<unk>')
    tokenizer.fit_on_texts(sas['full_text'])

    return tokenizer

# def tune_model(embedding_size=100,vocab_size=20000,test_size=1000,lr=0.0001):
#     M=get_embedding_map('glove/glove.twitter.27B.{}d.txt'.format(embedding_size))
#     sas=prep_data()
#     max_tweet_len=sas['tweet_len'].max()

#     tokenizer=get_tokenizer(sas,vocab_size)

#     sequences=tokenizer.texts_to_sequences(sas['full_text'])
#     X=pad_sequences(sequences,maxlen=max_tweet_len)
#     y=sas['is_good_tweet'].values

#     X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=test_size)

#     E=np.zeros((vocab_size,embedding_size))
#     for word,index in tokenizer.word_index.items():
#         if index>vocab_size-1:
#             break
#         else:
#             if word in M:
#                 E[index]=M[word]

#     m=tf.keras.models.Sequential([
#     Embedding(vocab_size,
#               embedding_size,
#               embeddings_initializer=Constant(E),
#               input_length=max_tweet_len,
#               trainable=True),
#     Bidirectional(LSTM(64,activation='relu')),
#     Dropout(0.2),
#     Dense(1,activation='sigmoid')])

#     m.compile(loss='binary_crossentropy',
#               optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
#               metrics=[tf.keras.metrics.AUC(curve='PR')])

#     m.fit(X_train,y_train,
#           batch_size=32,
#           epochs=10,
#           validation_split=0.2)

#     y_hat=m.predict(X_test)
#     print('test average precision:',average_precision_score(y_test,y_hat))
#     print('test roc auc:',roc_auc_score(y_test,y_hat))

def fit_model(embedding_size=100,vocab_size=20000,test_size=1000,lr=0.0001):
    M=get_embedding_map('glove/glove.twitter.27B.{}d.txt'.format(embedding_size))
    sas=prep_data()
    max_tweet_len=sas['tweet_len'].max()

    tokenizer=get_tokenizer(sas,vocab_size)

    sequences=tokenizer.texts_to_sequences(sas['full_text'])
    X=pad_sequences(sequences,maxlen=max_tweet_len)
    y=sas['is_good_tweet'].values

    E=np.zeros((vocab_size,embedding_size))
    for word,index in tokenizer.word_index.items():
        if index>vocab_size-1:
            break
        else:
            if word in M:
                E[index]=M[word]

    m=tf.keras.models.Sequential([
    Embedding(vocab_size,
              embedding_size,
              embeddings_initializer=Constant(E),
              input_length=max_tweet_len,
              trainable=True),
    Bidirectional(LSTM(64,activation='relu')),
    Dropout(0.2),
    Dense(1,activation='sigmoid')])

    m.compile(loss=tf.keras.losses.BinaryCrossentropy(),
              optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
              metrics=[tf.keras.metrics.AUC(curve='PR')])

    m.fit(X,y,batch_size=32,epochs=10)

    m.save('saved_models/scoring_model.h5')
    print('saved model:','saved_models/scoring_model.h5')

if __name__=='__main__':
    fit_model()
