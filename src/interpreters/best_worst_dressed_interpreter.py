import re
from collections import Counter

import spacy


def dress_tweets(data):
    space_chars = ['-', '/', '&', '@']
    res = []
    for tweet in data:
        if 'RT @' not in tweet['text']:
            for char in space_chars:
                tweet['text'] = tweet['text'].replace(char, ' ')
            res.append(tweet['text'])
    return res
  
def best_worst_dressed(data):
    nlp = spacy.load('en_core_web_sm')
    tweets = dress_tweets(data)
    allowed = ['amazing dress|beautiful dress|best dressed|best dress','worst dressed|ugly dress|bad dress']
    all_tags = [ re.findall('#([a-zA-Z0-9_]{1,50})', tweet['text']) for tweet in data ]
    name = Counter(all_tags).most_common(1).lower()

    for i in allowed:
        to_count = []
        for t in tweets:
            index = re.search(i, t.lower())
            if index:
                tags = nlp(t[:index.start()])
                for ent in tags.ents:
                    if (ent.label_ == 'PERSON' and 
                        ent.text.lower().replace(' ', '') != name):
                        to_count.append(ent.text)

    top2 = Counter(to_count).most_common(2)  
    print(f'Best Dressed - {top2[0]}')
    print(f'Worst Dressed - {top2[1]}')
