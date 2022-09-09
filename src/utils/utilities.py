import re
import string

import imdb
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import PorterStemmer

from utils import imdb_api


def tokenize(str):
    return word_tokenize(str)

def format_return(seq, return_as_str):
    is_str = type(seq) is str

    if (return_as_str == is_str):
        return seq
    elif return_as_str and not is_str:
        return ' '.join(seq)
    else:
        return tokenize(seq)

def lower(seq, return_as_str=False):
    lower_str, lower_lst = None, None

    if type(seq) is str:
        lower_str = seq.lower()
    else:
        lower_lst = list(map(str.lower, seq))

    return format_return(lower_str or lower_lst, return_as_str)

def remove_stop_words(seq, return_as_str=False):
    if type(seq) is str:
        seq = tokenize(seq)

    stops = set(stopwords.words('english'))
    tokenized_no_sw = [token for token in seq if token not in stops]

    return format_return(tokenized_no_sw, return_as_str)

def stem(seq, return_as_str=False):
    if type(seq) is str:
        seq = tokenize(seq)

    ps = PorterStemmer()
    stemmed_lst = list(map(ps.stem, seq))
    
    return format_return(stemmed_lst, return_as_str)

def remove_punctuation(seq, return_as_str=False):
    if type(seq) is str:
        seq = seq.translate(str.maketrans('', '', string.punctuation))
    else:
        seq = [token.translate(str.maketrans('', '', string.punctuation)) for token in seq]

    return format_return(seq, return_as_str)


def _increment_dict_val(result_dict, key, val):
    if key not in result_dict:
        result_dict[key] = val
    else:
        result_dict[key] += val

def _increment_award_presenter(award_dict, award, name, val):
    if award not in award_dict:
        award_dict[award] = dict()
        award_dict[award][name] = val
    if name not in award_dict[award]:
        award_dict[award][name] = val
    else:
        award_dict[award][name] += val

def awards_to_people_parser(award_ppl_dict, year, and_odds=None):
    nltk_dict = dict()
    ia = imdb.IMDb()
    result_dict = dict()
    correct_names_dict = dict()
    for award, people_dict in award_ppl_dict.items():
        if len(people_dict) == 0:
            result_dict[award] = ''
            continue
            
        sorted_people = sorted(people_dict.items(), key=lambda x: x[1], reverse=True)
        for item in sorted_people:
            name = item[0]
            val = item[1]
            # perform imdb check and value mutation

            found_name = imdb_api.imdb_get_similar(name, ia, year, type="person")
            num_nnp = 0
            if found_name == None or found_name == '': continue

            #check if proper noun by nltk
            if found_name != None:
                found_list = found_name.split(" ")
                uppercase_found_list = []
                for i in found_list:
                    var = i
                    uppercase_found_list.append(var.capitalize())
                name_list_uppercased = " ".join(uppercase_found_list)
                        
                # perform nltk check and value mutation
                if name in nltk_dict:
                    l1 = nltk_dict[name]
                else:
                    name_token = tokenize(name_list_uppercased)
                    l1 = nltk.pos_tag(name_token)
                    nltk_dict[name] = l1
                for element in l1:
                    if element[1] != 'NNP':
                        val = val * 0.25
                    else:
                        num_nnp += 1
            if num_nnp == 0: continue

            
            # if imdb marked it as a nickname, remove nickname marker
            if found_list[-1] == "nickname": 
                found_list.pop()
                new_found_list = []
                for element in found_list:
                    if element != '': new_found_list.append(element)
                found_list = new_found_list
                found_name = " ".join(new_found_list)
            
            #check and update and_odds
            if and_odds != None and name in and_odds:
                if and_odds[name] > 2:
                    if found_name in and_odds:
                        and_odds[found_name] += and_odds[name]
                        val += 5
                    else:
                        and_odds[found_name] = and_odds[name]
                        val += 5

            # if good length for name and search result is perfect match, increase weight
            name_list = name.split(" ")
            if len(found_list) == len(name_list):
                if len(found_list) == 2:
                    val = val * 5
                    if found_list == name_list:
                        val = val * 5
                # if a less common length for name, and search result is perfect match, increase weight
                if len(found_list) == 3 and num_nnp != 0:
                    if found_list == name_list:
                        val = val * 5

            # check for similarity of name
            if found_name == name:
                if len(found_name) > 1:
                    val = val * 5
            else:
                for part in found_list:
                    if part == name:
                        val = val * 3
            _increment_award_presenter(correct_names_dict, award, found_name, val)

    for award, person_dict in correct_names_dict.items():
        possible_ands = []
        for person, score in person_dict.items():
            if person in and_odds:
                if and_odds[person] > 0:
                    possible_ands.append([person, score])
        sorted(possible_ands, key=lambda x: x[1], reverse=True)
        max_persons = [None, None]
        max_scores = [0, 0]
        
        for person, score in person_dict.items():
            if score > max_scores[0]:
                max_persons[1], max_scores[1] = max_persons[0], max_scores[0]
                max_persons[0], max_scores[0] = person, score
            elif score > max_scores[1]:
                max_persons[1], max_scores[1] = person, score


        
        # if we think it's presented by two people
        if max_persons[0] in and_odds:
            if max_persons[1] in and_odds:
                result_dict[award] = max_persons
        elif max_persons[1] in and_odds:
            result_dict[award] = [possible_ands[0][0], possible_ands[1][0]]
        # otherwise
        else:
            result_dict[award] =  [max_persons[0]]#[max_persons[0]]
    return result_dict
        #sort by value
        #check for whether or not word is nltktagged as NNP, not tagged as NNP --> .25x
        #if exact match for search term, add 5x value
        #if shared word with search term, 2x value

def empasize_shared_dictvals(award_entity_dict):

    for award, entity_dict in award_entity_dict.items():
        # for the top 10 potential names in each award dict, increase their values based on how many words they share
        # with other found entities
        sorted_entities = sorted(entity_dict.items(), key=lambda x: x[1], reverse=True)
        cutoff_index = min(len(sorted_entities), 10)
        sorted_entities = sorted_entities[0:cutoff_index]
        for likely_entity in sorted_entities:
            likely_name = likely_entity[0]
            likely_val = likely_entity[1]
            likely_name_s = likely_name.split(" ")
            for other_entity in sorted_entities:
                other_name = other_entity[0]
                other_val = other_entity[1]
                if likely_name in other_name:
                    if len(likely_name_s) > 1:
                        likely_val += other_val

            award_entity_dict[award][likely_entity[0]] = likely_val


def awards_to_winner_parser(award_winner_dict, year):
    nltk_dict = dict()
    ia = imdb.IMDb()
    result_dict = dict()
    correct_names_dict = dict()

    #empasize_shared_dictvals(award_winner_dict)

    for award, entity_dict in award_winner_dict.items():
        if len(entity_dict) == 0:
            result_dict[award] = ''
            continue

        sorted_people = sorted(entity_dict.items(), key=lambda x: x[1], reverse=True)

        for item in sorted_people[0:4]:
            name = item[0]
            val = item[1]
            # perform imdb check and value mutation

            found_name_list = imdb_api.imdb_get_similar_entity(name, ia, year) 
            for found_name in found_name_list:
                if found_name == None: continue

                # if good length for name and search result is perfect match, increase weight
                found_name_split = found_name.split(" ")
                name_split = name.split(" ")
                # if imdb marked it as a nickname, remove nickname marker
                if found_name_split[-1] == "nickname": 
                    found_name_split.pop()
                    new_found_name_list = []
                    for element in found_name_split:
                        if element != '': new_found_name_list.append(element)
                    found_name_split = new_found_name_list
                    found_name = " ".join(new_found_name_list)



                if len(found_name_split) == len(name_split):
                    if len(found_name_split) > 1:
                        val = val * 2
                    else:
                        val = val * 1.5


                        
                # check for single non-verb non-noun names
                if len(found_name_split) == 1:
                    if found_name_split[0] == "Best" or found_name_split[0] == "best": continue
                    found_name_no_punctuation = re.sub(r'[^\w\s]', '', found_name_split[0])
                    if found_name_no_punctuation in nltk_dict:
                        l1 = nltk_dict[found_name_no_punctuation]
                    else:
                        name_token = tokenize(found_name_no_punctuation)
                        l1 = nltk.pos_tag(name_token)
                        nltk_dict[name] = l1
                    # if title is just a part of speech like 'the' or 'by', skip
                    if l1[0][1] == 'CC' or l1[0][1] == 'DT'or l1[0][1] == 'IN':
                        continue

                # check for similarity of name
                if found_name == name:
                    if len(found_name) > 1:
                        val = val * 2
                    else:
                        val = val * 1.5
                else:
                    for part in found_name_list:
                        if part == name:
                            val = val * 1.25
                _increment_award_presenter(correct_names_dict, award, found_name, val)

    for award, person_dict in correct_names_dict.items():
        sorted_entities = sorted(person_dict.items(), key=lambda x: x[1], reverse=True)
        result_entities = sorted_entities[0:5]

        # process subnames
        for entity_index in range(len(result_entities)):
            entity = result_entities[entity_index]
            for second_entity_index in range(len(result_entities)):
                second_entity = result_entities[second_entity_index]
                if is_subname(entity[0], second_entity[0]):
                    result_entities[second_entity_index] = (second_entity[0], entity[1] + second_entity[1])
        sorted_result_entities = sorted(result_entities, key=lambda x:x[1], reverse=True)
        result_dict[award] = sorted_result_entities
    # if something wins more than 3 categories, toss it (variety m-name)
    win_count = dict()
    for award, winner_list in result_dict.items():
        for entity in winner_list:
            _increment_dict_val(win_count, entity[0], 1)
    for award, winner_list in result_dict.items():
        if len(winner_list) != 0:
            for entity_index in range(len(winner_list)):
                entity = winner_list[entity_index]
                if entity[0] in win_count and win_count[entity[0]] > 2:
                    winner_list[entity_index] = [entity[0], 0]
            winner_list_sorted = sorted(winner_list, key=lambda x:x[1], reverse=True)
            result_dict[award] = winner_list_sorted[0][0]
    return result_dict
    # TODO: add way of scanning dict for commonly shared words, and increasing their weight.
def is_subname(subname, name):
    subname_list = subname.split(" ")
    name_list = name.split(" ")
    if len(subname_list) + 1 != len(name_list):
        return False
    for sub in subname_list:
        if sub in name_list:
            return True

# Finds person mentioned and tweet, first value is true for postive
def tweet_opinion(tweet):
    sia = SentimentIntensityAnalyzer()

    net_opinion = sia.polarity_scores(tweet)["compound"] > 0
    ents = [] # List of tuples, i.e. `PERSON, Bradley Cooper`
    for sent in nltk.sent_tokenize(tweet):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label'):
                ents.append((chunk.label(), chunk[0][0]))
    
    # Optional crude pass, return 1 person from ent list
    person_topic = None
    for ent in ents:
        if ent[0] == "PERSON":
            person_topic = ent[1]
            break
    return [net_opinion, person_topic]

# Get surrounding adjectives for word, can be used to check "Dressed"
# POS over wordnet pass
def topic_descriptors(tweet, target_word):
    index = (i for i,word in enumerate(tweet) if word==target_word)
    neighbor_words = []
    for i in index:
        neighbor_words.append(tweet[i-3:i]+tweet[i+1:i+4])
    adjective_tags = ["JJ", "JJR", "JJS"]
    neighbor_adjectives = [a[0] for a in nltk.pos_tag(" ".join(neighbor_words)) if a[1] in adjective_tags ]
    return neighbor_adjectives
