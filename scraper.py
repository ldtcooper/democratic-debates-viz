import requests
from bs4 import BeautifulSoup
import re
import operator

html_string = requests.get('https://www.washingtonpost.com/politics/2019/07/31/transcript-first-night-second-democratic-debate/').content
html_tree = BeautifulSoup(html_string, 'html.parser')

def filter_html(tag):
    # gets all p tags with no i tags in them
    if tag.name == 'p' and not tag.i:
        if re.match('\([A-Z ]+\)', tag.text):
            # filters out placeholders like '(APPLAUSE)' and '(LAUGHTER)'
            return False
        return True
    else:
        return False


p_collection = html_tree.find('article').find_all(filter_html)

# we don't want to include the moderators in our table
moderators = ['TAPPER', 'BASH', 'LEMON']
last_match = None
candidate_collections = {}
for p in p_collection:
    if p.string == None:
        continue
    tag_text = p.string.replace('\n', '')
    # grabs the name of the speaker
    tag_matcher = '^(([A-Z]+)( \(\?\))?): (.+)$'
    speaker_match = re.match(tag_matcher, tag_text)

    if speaker_match:
        # if there is a name in front, we know there is a new speaker
        name = speaker_match.group(2)
        last_match = name
        dialog = speaker_match.group(4)
    else:
        # otherwise, use the last name we saw
        name = last_match
        dialog = tag_text
    # transcript uses "health care" and "healthcare" interchangably
    dialog = dialog.replace('health care', 'healthcare')
    if name in moderators:
        # throw out moderator dialog
        last_match = name
        continue
    if name not in candidate_collections:
        candidate_collections[name] = [dialog]
    else:
        candidate_collections[name].append(dialog)
print(candidate_collections)
# word_frequencies = {'TOTAL': {}}
# for p in p_collection:
#     if p.string == None:
#         continue
#     tag_text = p.string.replace('\n', '')
#     tag_matcher = '^(([A-Z]+)( \(\?\))?): (.+)$'; # grabs the name of the speaker
#     speaker_match = re.match(tag_matcher, tag_text)
#     # some new p tags continue the last speaker's thought and don't have a name in front
#     if speaker_match:
#         # if there is a name in front, we know there is a new speaker
#         name = speaker_match.group(2)
#         last_match = name
#         dialog = speaker_match.group(4)
#     else:
#         # otherwise, use the last name we saw
#         name = last_match
#         dialog = tag_text
#     if name in moderators:
#         # throw out moderator dialog
#         last_match = name
#         continue
#     if name not in word_frequencies:
#         word_frequencies[name] = {}
#     # transcript uses "health care" and "healthcare" interchangably
#     word_list = dialog.replace('health care', 'healthcare').split(' ')
#     for word in word_list:
#         word = word.lower()
#         word = re.sub('[.,\?!"\d\$-]+', '', word)
#         if word == '':
#             continue
#         if word in word_frequencies[name]:
#             word_frequencies[name][word] += 1
#             word_frequencies['TOTAL'][word] += 1
#         else:
#             word_frequencies[name][word] = 1
#             word_frequencies['TOTAL'][word] = 1

# # scraped from https://en.wikipedia.org/wiki/Most_common_words_in_English
# common_words_list = ["the", "be", "is", "was", "were", "are", "am", "to", "of", "and", "a", "an", "in", "that", "that's", "have", "has", "had", "i", "i'm", "i've", "it", "it's", "for", "not", "on", "with", "he", "as", "you", "you're", "do", "don't", "did", "at", "this", "but", "his", "by", "from", "they", "they've", "they're", "we", "we've", "we're", "say", "her", "she", "or", "will", "my", "one", "all", "would", "there", "there's", "their", "what", "so", "up", "out", "if", "about", "who", "get", "got", "which", "go", "me", "when", "make", "can", "can't", "like", "time", "no", "just", "him", "know", "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "those", "give", "day", "most", "us"]
# common_words = set(common_words_list)
# sorted_candidate_frequencies = {}
#
# for candidate, freqs in word_frequencies.items():
#     sorted_frequencies = sorted(freqs.items(), key=operator.itemgetter(1), reverse=True)
#     sorted_candidate_frequencies[candidate] = []
#     for el in sorted_frequencies:
#         if el[0] not in common_words:
#             sorted_candidate_frequencies[candidate].append(el)
#
# print(sorted_frequencies)
