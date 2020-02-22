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
moderators = ['tapper', 'bash', 'lemon']
last_match = None
debate_collection = []
for p in p_collection:
    if p.string == None:
        continue
    tag_text = p.string.replace('\n', '')
    # grabs the name of the speaker
    tag_matcher = '^(([A-Z]+)( \(\?\))?): (.+)$'
    speaker_match = re.match(tag_matcher, tag_text)

    if speaker_match:
        # if there is a name in front, we know there is a new speaker
        name = speaker_match.group(2).lower()
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
    debate_collection.append({'candidate': name, 'dialog': dialog})
print(debate_collection)
