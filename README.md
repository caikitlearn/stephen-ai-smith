# Stephen A.I. Smith
``https://caikitlearn.com/stephen-ai-smith``

## Step 1: get Twitter data
- ``twitter_scraping/scrape.py`` collects the tweet IDs
- ``twitter_scraping/get_metadata.py`` reads in the tweet IDs and collects the corresponding metadata
- ``process_csvs.py`` compiles all the data

## Step 2: train GPT-2
- use ``data/stephenasmith_gpt2.csv`` as training data
- follow [this](https://colab.research.google.com/drive/1RugXCYDcMvSACYNt9j0kB6zzqRKzAbBn) template notebook by Max Woolf

## Step 3 (optional): score the generated tweets
- ``scoring_model.py`` trains the model
- ``get_top_100.py`` saves the top 100 highest scoring tweets
