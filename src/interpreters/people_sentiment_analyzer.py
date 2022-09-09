import random

from utils import utilities


def analyze_sentiment(host, host_hit_count, host_analysis, t):
    sentiment = utilities.tweet_opinion(t)
    sentiment_score = sentiment[0]
    found_person = None
    if sentiment[1] != None: found_person = sentiment[1].lower()
    if found_person == host:
        host_hit_count[host] += 3
        host_analysis[host] += 3*sentiment_score
    else:
        host_hit_count[host] += 1
        host_analysis[host] += sentiment_score


def analyze_people(host_list, data):
    if host_list == []: return None
    relevant_tweets = dict()
    host_hit_count = dict()
    host_analysis = dict()
    for host in host_list:
        host_analysis[host] = 1
        host_hit_count[host] = 1
        relevant_tweets[host] = []
    for post in data:
        t = post['text']
        t_lower = t.lower()
        for host in host_list:
            if host in t_lower:
                relevant_tweets[host].append(t)

    for host, value in relevant_tweets.items():
        if len(value) > 2001:
            selected_tweets = random.choices(value, k=2000)
        else:
            selected_tweets = value
        for tweet in selected_tweets:
            analyze_sentiment(host, host_hit_count, host_analysis, tweet)
    for host, value in host_analysis.items():
        host_analysis[host] = round(value / host_hit_count[host], 4)

    return host_analysis
