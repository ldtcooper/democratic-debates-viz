import requests
import bs4
import re
import operator
from typing import Tuple, Optional, List

# types
ResultSet = bs4.element.ResultSet
Tag = bs4.element.Tag
DebateRecordTuple = Tuple[str, str, bool]

def filter_html(tag: Tag) -> bool:
    """
    Allows BeautifulSoup to get all <p> tags without nested <i> tags
    and filter them for 'sound effect' text
    """
    # gets all p tags with no i tags in them
    if tag.name == 'p' and not tag.i:
        if re.match('\([A-Z ]+\)', tag.text):
            # filters out placeholders like '(APPLAUSE)' and '(LAUGHTER)'
            return False
        return True
    else:
        return False

def match_name_and_dialog(tag_text: str) -> Optional[bool]:
    """
    Regex matcher to separate the name of the speaker from what they said
    if there is a stated speaker
    """
    tag_matcher = '^(([A-Z]+)( \(\?\))?): (.+)$'
    return re.match(tag_matcher, tag_text)

def build_tuple(name: str, dialog: str, replace_match: bool) -> DebateRecordTuple:
    """
    Cleans dialog and packs up various parts of the match into a tuple
    """
    # transcript uses "health care" and "healthcare" interchangably
    dialog = dialog.replace('health care', 'healthcare')
    return (name, dialog, replace_match)

def extract_name_and_dialog(p_tag: Tag, last_match: str) -> DebateRecordTuple:
    """
    Takes in a parsed BeautifulSoup tag and turns it into a tuple of who
    said what and whether or not we need to redajust the store last speaker
    in debate_scraper
    """
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
    return build_tuple(name, dialog, replace_match)

def get_html(url: str) -> ResultSet:
    """
    Makes a GET request to the URL of the debate transcript and
    parses it with BeautifulSoup
    """
    html_string = requests.get(url).content
    html_tree = bs4.BeautifulSoup(html_string, 'html.parser')
    return html_tree.find('article').find_all(filter_html)

def debate_scraper(url: str, moderators: List[str]) -> List[dict]:
    """
    Puts together a list of dicts from the parsed debate HTML
    where each dict represents a record of who said what
    """
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
