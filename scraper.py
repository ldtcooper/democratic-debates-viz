import requests
from bs4 import BeautifulSoup
import re
import operator


def filter_html(tag):
    # gets all p tags with no i tags in them
    if tag.name == 'p' and not tag.i:
        if re.match('\([A-Z ]+\)', tag.text):
            # filters out placeholders like '(APPLAUSE)' and '(LAUGHTER)'
            return False
        return True
    else:
        return False

def match_name_and_dialog(tag_text):
        # grabs the name of the speaker
        tag_matcher = '^(([A-Z]+)( \(\?\))?): (.+)$'
        return re.match(tag_matcher, tag_text)

def extract_name_and_dialog(p_tag, last_match):
    tag_text = p_tag.string.replace('\n', '')
    speaker_match = match_name_and_dialog(tag_text)
    if speaker_match:
        # if there is a name in front, we know there is a new speaker
        name = speaker_match.group(2).lower()
        replace_match = True
        dialog = speaker_match.group(4)
    else:
        # otherwise, use the last name we saw
        name = last_match
        replace_match = False
        dialog = tag_text
    # transcript uses "health care" and "healthcare" interchangably
    return (name, dialog.replace('health care', 'healthcare'), replace_match)

def get_html(url):
    html_string = requests.get(url).content
    html_tree = BeautifulSoup(html_string, 'html.parser')
    return html_tree.find('article').find_all(filter_html)

def debate_pipeline(url, moderators):
    p_collection = get_html(url)
    debate_collection = []
    last_match = None
    for p in p_collection:
        if p.string == None:
            continue
        name, dialog, replace_match = extract_name_and_dialog(p, last_match)
        if replace_match:
            last_match = name
        debate_collection.append({'speaker': name, 'dialog': dialog, 'moderator': (name in moderators)})
    return debate_collection

print(debate_pipeline('https://www.washingtonpost.com/politics/2019/07/31/transcript-first-night-second-democratic-debate/', ['tapper', 'bash', 'lemon']))
