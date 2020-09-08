import requests
import pandas as pd
import bs4
from typing import List, Dict
import re

Tag = bs4.element.Tag

bracket_text = re.compile(r'\[.+\]')


def get_tags_from_url(url: str) -> List[Tag]:
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, 'html.parser')
    transcript = soup.find('div', {'id': 'transcription'}).find_all('p')
    return transcript


def remove_bracket_text(dialog: str) -> str:
    """
    Non dialog portions are denoted by square brackets e.g. "[inaudible at 3:14]"
    This function takes those out
    """
    clean_string = re.sub(bracket_text, '', dialog)
    return clean_string


def split_tag(tag: Tag) -> List[str]:
    """
    The speaker is split from their dialog by a single <br/>
    This function splits each p tag based on that
    """
    speaker, dialog = tag.decode_contents().split('<br/>')
    # remove colon from after speaker name
    speaker = speaker[:-1]
    return [speaker, remove_bracket_text(dialog)]


def convert_transcrit_to_list(transcript: List[Tag]) -> List[List[str]]:
    dialog_list = []
    for p in transcript:
        row = split_tag(p)
        dialog_list.append(row)
    return dialog_list


def add_moderator_row(data: List[List[str]], moderators: List[str]) -> List[List[str]]:
    for row in data:
        speaker = row[0]
        is_moderator = speaker in moderators
        row.append(is_moderator)
    return data


url = 'https://www.rev.com/blog/transcripts/transcript-from-first-night-of-democratic-debates'

# moderator list source: https://www.nbcnews.com/politics/2020-election/nbc-announces-five-moderators-first-democratic-debate-n1016106
moderators = [
    'Lester Holt',
    'Savannah G.',
    'Chuck Todd',
    'Rachel Maddow',
    'Jose D.B.',
]

transcript = get_tags_from_url(url)
dialog_list = convert_transcrit_to_list(transcript)
print(add_moderator_row(dialog_list, moderators))
