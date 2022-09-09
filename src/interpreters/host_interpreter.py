import re


def increment_dict_val(target_dict, key, val):
    if key not in target_dict:
        target_dict[key] = val
    else:
        target_dict[key] += val

def find_host(data):
    has_cohost_dict = dict() 
    host_dict = dict()
    for post in data:
        tweet = re.sub(r'[^\w\s]', '', post['text'])
        t_lower = tweet.lower()
        tl_split = tweet.split()
        tl_split_lower = t_lower.split()
        #if has hosted by and does not have words that indicate inaccuracy
        if all(["hosted" in tl_split_lower, "by" in tl_split_lower, "should" not in tl_split_lower, "could" not in tl_split_lower, "wish" not in tl_split_lower]):
            name_index = tl_split_lower.index("by") + 1
            
            # if by is the last word, not useful, go to next post
            if not name_index + 2 < len(tl_split_lower):
                continue
            # find 'and' to see if listing both hosts
            name_index_2 = -1
            if "amp" in tl_split_lower and tl_split_lower.index("amp") + 2 < len(tl_split_lower):
                name_index_2 = tl_split_lower.index("amp") + 1

            if "and" in tl_split_lower and tl_split_lower.index("and") + 2 < len(tl_split_lower):
                name_index_2 = tl_split_lower.index("and") + 1

            # if 'and' after 'hosted by'
            if name_index_2 > name_index:
                first_name_1 = tl_split[name_index]
                last_name_1 = tl_split[name_index + 1]
                first_name_2 = tl_split[name_index_2]
                last_name_2 = tl_split[name_index_2 + 1]
                value = 1
                if all([first_name_1[0].isupper(), last_name_1[0].isupper(), first_name_2[0].isupper(), last_name_2[0].isupper()]):
                    value = 2
                name_1 = first_name_1.capitalize() + " " + last_name_1.capitalize()
                name_2 = first_name_2.capitalize() + " " + last_name_2.capitalize()
                increment_dict_val(host_dict, name_1, value)
                increment_dict_val(host_dict, name_2, value)
                increment_dict_val(has_cohost_dict, name_1, value)
                increment_dict_val(has_cohost_dict, name_2, value)
            else:
                name_1 = tl_split[name_index].capitalize() + " " + tl_split[name_index + 1].capitalize()
                increment_dict_val(host_dict, name_1, 1)
    sorted_host_dict = sorted(host_dict.items(), key=lambda x: x[1], reverse=True)
    hosts = []
    most_likely_host = sorted_host_dict[0][0]
    most_likely_weight = sorted_host_dict[0][1]
    # if 1/5 of the most likely host tweets also mention a second host
    if has_cohost_dict[most_likely_host] < most_likely_weight * 5:
        hosts.append(sorted_host_dict[0][0])
        hosts.append(sorted_host_dict[1][0])
    else:
        hosts.append(sorted_host_dict[0][0])
    for index in range(len(hosts)):
        hosts[index] = hosts[index].lower()
    return hosts
