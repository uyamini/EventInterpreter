import re
import string

import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tokenize import word_tokenize
from nltk.tree import Tree


def _increment_dict_val(target_dict, key, val):
    if key not in target_dict:
        target_dict[key] = val
    else:
        target_dict[key] += val

def _has_end_punctuation(word):
    return len(word) > 0 and word[-1] in string.punctuation and "-" not in word

def _has_link_indicator(next_word):
    return '\\' in next_word or '/' in next_word or 'http' in next_word or '#' in next_word

def find_potential_awards(t, award_name_dict, tnp, tnp_split, tnp_l, tnp_l_split):
    t_split = t.split(" ")

    best_index = tnp_l_split.index("best")
    temp_index = best_index
    award_name = ''
    num_dashes = 0
    immediate_stop = False
    while temp_index + 1 < len(t_split) and not _has_end_punctuation(t_split[temp_index]) and num_dashes == 0:
        next_word = t_split[temp_index]
        if next_word != '-':
            next_word = re.sub(r'[^\w\s]', '', t_split[temp_index])
        else:
            next_word = '-'
        if _has_link_indicator(next_word): 
            immediate_stop = True
            break
        if next_word == '-': num_dashes += 1
        next_word = next_word.lower()
        award_name += f' {next_word}'
        temp_index += 1

    if not immediate_stop:
        final_word = re.sub(r'[^\w\s]', '', t_split[temp_index])
        final_word = final_word.lower()
        award_name += f' {final_word}'
    award_name = award_name[1:]
    split_award_name = award_name.split(" ")
    if len(split_award_name) > 1: _increment_dict_val(award_name_dict, award_name, 1)

    
def find_potential_quote_awards(award_name_dict, t_split, t_l_split, keyword):
    best_word = keyword.lower()
    start_index = t_l_split.index(best_word)
    temp_index = start_index + 1
    award_name = 'best'
    immediate_stop = False
    while temp_index + 1 < len(t_split) and not _has_end_punctuation(t_split[temp_index]):
        next_word = t_split[temp_index]
        next_word = next_word.lower()
        if _has_link_indicator(next_word): 
            immediate_stop = True
            break
        award_name += f' {next_word}'
        temp_index += 1
    if not immediate_stop:
        final_word = re.sub(r'[^\w\s]', '', t_split[temp_index])
        final_word = final_word.lower()
        award_name += f' {final_word}'
    split_award_name = award_name.split(" ")

    if len(split_award_name) > 1: _increment_dict_val(award_name_dict, award_name, 5)


def find_awards(data, year=None):
    result = []
    award_name_dict = dict()
    
    for post in data:
        t = post['text']
        t_split = t.split(" ")
        tnp = re.sub(r'[^\w\s]', '', post['text'])
        tnp_l = tnp.lower()
        tnp_l_split = tnp_l.split(" ")
        tnp_split = tnp.split(" ")

        if 'Best' in tnp_split:
            find_potential_awards(t, award_name_dict, tnp, tnp_split, tnp_l, tnp_l_split)
        if '\'Best' in t_split:
            t_l = t.lower()
            t_l_split = t_l.split(" ")
            find_potential_quote_awards(award_name_dict, t_split, t_l_split, keyword='\'Best')
        if '\"Best' in t_split:
            t_l = t.lower()
            t_l_split = t_l.split(" ")
            find_potential_quote_awards(award_name_dict, t_split, t_l_split, keyword='\"Best')

    #TODO: filter dictionary for sub-awards
    
    sorted_award_names = sorted(award_name_dict.items(), key=lambda x: x[1], reverse=True)
    top_sorted_awards = sorted_award_names[0:50]

    # cut off potential names at verbs
    for index in range(len(top_sorted_awards)):
        current_award = top_sorted_awards[index]
        award_name = current_award[0]
        name_token = word_tokenize(award_name)
        l1 = nltk.pos_tag(name_token)
        for index2 in range(len(l1)):
            element = l1[index2] 
            if ('VB' == element[1] or 'VBZ' == element[1]) and (element[1] != 'VBN' and element[1] != 'VBG'):
                award_name_split = award_name.split(" ")
                name_before_verb = " ".join(award_name_split[0:index2])
                top_sorted_awards[index] = (name_before_verb, top_sorted_awards[index][1])
                break

    #check for overlapping awards
    for index in range(len(top_sorted_awards)):
        primary_award = top_sorted_awards[index]
        primary_award_name = primary_award[0]
        for index2 in range(len(top_sorted_awards)):
            secondary_award = top_sorted_awards[index2]
            secondary_award_name = secondary_award[0]
            if secondary_award_name in primary_award_name and len(secondary_award_name) + 2 < len(primary_award_name):
                top_sorted_awards[index] =  (top_sorted_awards[index][0], top_sorted_awards[index][1] + int(secondary_award[1] / 2))
                top_sorted_awards[index2] = (top_sorted_awards[index2][0], int(top_sorted_awards[index2][1] * 0.5))
    parsed_top_sorted_awards = sorted(top_sorted_awards, key=lambda x: x[1], reverse=True)
    parsed_top_sorted_awards = parsed_top_sorted_awards[:25]
    for award in parsed_top_sorted_awards:
        result.append(award[0])
    result_nltkchecked = list(map(removenames, result))
    final_list = [result_nltkchecked[i] for i in range(len(result_nltkchecked))]
    return final_list

def removenames(text):
    nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
    for nltk_result in nltk_results:
        if type(nltk_result) == Tree:
            name = ''
            for nltk_result_leaf in nltk_result.leaves():
                name += nltk_result_leaf[0] + ' '
            print('Type: ', nltk_result.label(), 'Name: ', name)
            text = text.replace(nltk_result.text, '')
    return text
