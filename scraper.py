import requests
import bs4
import re
import operator
from typing import Tuple, Optional, List

# types
ResultSet = bs4.element.ResultSet
Tag = bs4.element.Tag

def filter_html(tag: Tag) -> bool:
    # gets all p tags with no i tags in them
    if tag.name == 'p' and not tag.i:
        if re.match('\([A-Z ]+\)', tag.text):
            # filters out placeholders like '(APPLAUSE)' and '(LAUGHTER)'
            return False
        return True
    else:
        return False

def match_name_and_dialog(tag_text: str) -> Optional[bool]:
        # grabs the name of the speaker
        tag_matcher = '^(([A-Z]+)( \(\?\))?): (.+)$'
        return re.match(tag_matcher, tag_text)

def extract_name_and_dialog(p_tag: Tag, last_match: str) -> Tuple[str, str, bool]:
    tag_text = p_tag.string.replace('\n', '')
    speaker_match = match_name_and_dialog(tag_text)
    if speaker_match:
        # if there is a name in front, we know there is a new speaker
        name = speaker_match.group(2).lower()
        dialog = speaker_match.group(4)
        replace_match = True
    else:
        # otherwise, use the last name we saw
        name = last_match
        dialog = tag_text
        replace_match = False
    # transcript uses "health care" and "healthcare" interchangably
    return (name, dialog.replace('health care', 'healthcare'), replace_match)

def get_html(url: str) -> ResultSet:
    html_string = requests.get(url).content
    html_tree = bs4.BeautifulSoup(html_string, 'html.parser')
    return html_tree.find('article').find_all(filter_html)

def debate_scraper(url: str, moderators: List[str]) -> List[dict]:
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

debate_scraper('https://www.washingtonpost.com/politics/2019/07/31/transcript-first-night-second-democratic-debate/', ['tapper', 'bash', 'lemon'])
