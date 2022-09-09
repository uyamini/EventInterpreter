import re

from utils import utilities


def increment_dict_val(target_dict, key, val):
    if key not in target_dict:
        target_dict[key] = val
    else:
        target_dict[key] += val

def increment_award_presenter(award_dict, award, name, val):
    if name not in award_dict[award]:
        award_dict[award][name] = val
    else:
        award_dict[award][name] += val

def has_presenter_words(t_split):
    result = []
    if 'presented' in t_split:
        result.append('presented')
    if 'presents' in t_split:
        result.append('presents')
    if 'presenting' in t_split:
        result.append('presenting')
    if 'present' in t_split:
        result.append('present')
    return result

def has_keyword_words(t_split, wordlist):
    result = []
    for word in wordlist:
        if word in t_split:
            result.append(word)
    return result

def no_uncertain_words(t_split):
    return all(['should' not in t_split, 'wish' not in t_split, 'would' not in t_split])

def find_matched_awards(awards, t_split, winners_dict):
    max_weight = 0
    matched_award = None
    # check for similar award names
    for award_vector in awards:
        award_no_stop = award_vector[1]
        weight = 0
        for word in award_no_stop:
            if word in t_split:
                weight += 1
        if weight >= int(len(award_no_stop) / 2) and weight > max_weight:
            max_weight = weight
            matched_award = award_vector
    if matched_award != None:
        return matched_award
    # if no award matched by award name, try by winner name
    for winner_name, award_and_relation in winners_dict.items():
        if winner_name in t_split:
            pass
    
    return None

def backward_check_for_names_from_index(index, t_split, dense_t_split, tl_split_lower, award_dict, and_odds, matched_award, has_and=False):
    #look for single presenter
    start_index = index + 1
    name1_list = []
    name1_list_caps = []
    # TODO: STOP CHECK AT ANY FORM OF PUNCTUATION
    while start_index >= 0:
        start_index -= 1
        start_word = t_split[start_index]
        if start_word not in dense_t_split: continue

        temp_index = start_index
        while temp_index >= 0 and t_split[temp_index] in dense_t_split:
            # check for odd cases
            new_word = t_split[temp_index]
            if name1_list != []:
                if name1_list_caps[0][0].isupper() and name1_list_caps[0][1].islower():
                    if len(new_word) > 1:
                        if new_word[0].islower() or new_word[1].isupper():
                            break
            # check for non-alphabetical
            if not new_word.isalpha(): break

            # check for name length
            if len(name1_list) > 2: break

            # check for name component length:
            if len(new_word) < 3: break

            # append new word
            name1_list.append(tl_split_lower[temp_index])
            name1_list_caps.append(new_word)
            temp_index -= 1
        name1_list.reverse()
        name1 = ""
        for word in name1_list:
            name1 += word + " "
        if name1 != "":
            name1 = name1[:-1]
            if has_and: 
                increment_dict_val(and_odds, name1, 1)

            increment_award_presenter(award_dict, matched_award, name1, 1) 
        name1_list = []

def backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds, keyword):
        keyword_index = tl_split_lower.index(keyword)
        dense_t_split_lower = []
        for word in dense_t_split:
            dense_t_split_lower.append(word.lower())

        if keyword_index == 0: return

        first_potential_nameword = dense_t_split[dense_t_split_lower.index(keyword) - 1]
        name1_index = t_split.index(first_potential_nameword)
        #name1_index = keyword_index - 1
        name2_index = None

        # if indicator of multiple presenters, look for multiple presenters
        bef_keyword_lower = tl_split_lower[0:name1_index]
        if ("amp" in bef_keyword_lower and bef_keyword_lower.index("amp") <= name1_index - 1):
            name2_index = bef_keyword_lower.index("amp")
        if ("and" in bef_keyword_lower and bef_keyword_lower.index("and") <= name1_index - 1):
            name2_index = bef_keyword_lower.index("and")

        if name2_index != None:
            #look for multiple presenters
            backward_check_for_names_from_index(name1_index, t_split, dense_t_split, tl_split_lower, award_dict, and_odds, matched_award, has_and=True)
            backward_check_for_names_from_index(name2_index, t_split, dense_t_split, tl_split_lower, award_dict, and_odds, matched_award, has_and=True)
        else:
            backward_check_for_names_from_index(name1_index, t_split, dense_t_split, tl_split_lower, award_dict, and_odds, matched_award) 
        return


def process_presented(t_split, tl_split_lower, award_dict, matched_award, and_odds):
    dense_t_split = utilities.remove_stop_words(t_split)
    if "by" in t_split:
        name1_index = tl_split_lower.index("by") + 1
                        
        # if by is the last word, not useful, go to next post
        if not name1_index + 2 < len(tl_split_lower): return

        name_1 = t_split[name1_index].capitalize() + " " + t_split[name1_index + 1].capitalize()
        increment_award_presenter(award_dict, matched_award, name_1, 1)
    else:
        backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds, "presented")    

def process_presenting(t_split, tl_split_lower, award_dict, matched_award, and_odds):
    dense_t_split = utilities.remove_stop_words(t_split)
    backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds, "presenting")

def process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword, type='presenters'):
    dense_t_split = utilities.remove_stop_words(t_split)
    if type == 'presenters':
        backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds, keyword)
    if type == 'winners':
        backward_check_for_winners(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds, keyword)

def process_present(t_split, tl_split_lower, award_dict, matched_award, and_odds):
    dense_t_split = utilities.remove_stop_words(t_split)
    backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds,"present")

def process_presenter(t_split, tl_split_lower, award_dict, matched_award, and_odds):
    dense_t_split = utilities.remove_stop_words(t_split)
    backward_check_for_names(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds,"presenter")


def find_presenters(data, awards_official, year):
    # get awards and award_no_stop
    awards = [[awards_official[i], utilities.remove_stop_words(awards_official[i])] for i in range(len(awards_official))]
    and_odds = dict()
    # TODO: get winners
    winners_dict = dict()

    award_dict = dict()
    for award in awards:
        award_dict[award[0]] = dict()
    
    for post in data:
        tweet = re.sub(r'[^\w\s]', '', post['text'])
        t_lower = tweet.lower()
        t_split = tweet.split()
        tl_split_lower = t_lower.split()
        #if has presented by and does not have words that indicate inaccuracy
        presenter_indicators = has_presenter_words(tl_split_lower)
        if presenter_indicators != [] and no_uncertain_words(tl_split_lower):
            matched_award_vector = find_matched_awards(awards, t_split, winners_dict)
            if matched_award_vector == None: continue
            matched_award = matched_award_vector[0]

            for present_word in presenter_indicators:
                if present_word == 'presented': process_presented(t_split, tl_split_lower, award_dict, matched_award, and_odds)
                if present_word == 'presents': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="presents")
                if present_word == 'presenting': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="presenting")
                if present_word == 'present': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="present")
                if present_word == 'presenter': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="presenter")

    
    result = utilities.awards_to_people_parser(award_dict, year, and_odds)
    return result

# FUTURE IMPROVEMENTS
# Better parsing of possible names in forward and backward checking with NLTK
# eliminating winners from consideration


def backward_check_for_winners(tl_split_lower, t_split, award_dict, matched_award, dense_t_split, and_odds, keyword):
        keyword_index = tl_split_lower.index(keyword)
        dense_t_split_lower = []
        for word in dense_t_split:
            dense_t_split_lower.append(word.lower())

        if keyword_index == 0: return
        name1_index = None
        nameword_index = keyword_index - 1
        while nameword_index >= 0:
            if t_split[nameword_index] in dense_t_split:
                first_potential_nameword = dense_t_split[dense_t_split.index(t_split[nameword_index])]
                name1_index = t_split.index(first_potential_nameword)
                break
            nameword_index -= 1
        #name1_index = keyword_index - 1
        if name1_index == None: return
        
        backward_check_for_names_from_index(name1_index, t_split, dense_t_split, tl_split_lower, award_dict, and_odds, matched_award)
        backward_check_for_movie_from_index(name1_index, t_split, dense_t_split, tl_split_lower, award_dict, and_odds, matched_award) 
        return

def find_winners(data, awards_official, year):
    # get awards and award_no_stop
    awards = [[awards_official[i], utilities.remove_stop_words(awards_official[i])] for i in range(len(awards_official))]
    and_odds = dict()
    # TODO: get winners
    winners_dict = dict()

    award_dict = dict()
    for award in awards:
        award_dict[award[0]] = dict()
    
    for post in data:
        tweet = re.sub(r'[^\w\s]', '', post['text'])
        t_lower = tweet.lower()
        t_split = tweet.split()
        tl_split_lower = t_lower.split()
        #if has presented by and does not have words that indicate inaccuracy
        won_indicators = has_keyword_words(tl_split_lower, ['won', 'win', 'wins', 'winning', 'winner'])
        if won_indicators != [] and no_uncertain_words(tl_split_lower):
            matched_award_vector = find_matched_awards(awards, t_split, winners_dict)
            if matched_award_vector == None: continue
            matched_award = matched_award_vector[0]

            for won_word in won_indicators:
                if won_word == 'won': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="won", type='winners')
                if won_word == 'win': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="win", type='winners')
                if won_word == 'wins': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="wins", type='winners')
                if won_word == 'winning': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="winning", type='winners')
                if won_word == 'winner': process_backwards_keyword(t_split, tl_split_lower, award_dict, matched_award, and_odds, keyword="winner", type='winners')
    result = utilities.awards_to_winner_parser(award_dict, year)
    return result
