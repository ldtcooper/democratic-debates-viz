import requests
import pandas as pd
import bs4
from typing import List, Dict
import re

Tag = bs4.element.Tag

# we're going to be removing a lot of things between brackets
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


def split_tag(tag: Tag) -> Dict[str, str]:
    """
    The speaker is split from their dialog by a single <br/>
    This function splits each p tag based on that
    """ 
    try:
        speaker, dialog = tag.decode_contents().split('<br/>')
        # remove everything after colon from after speaker name
        speaker = speaker.split(':')[0]
        return {'speaker': speaker, 'dialog': remove_bracket_text(dialog)}
    except ValueError as e:
        # No <br> means we can't unpack. Should only happen for non-dialog
        return None



def determine_moderator(speaker: str, moderators: List[str]) -> bool:
    return True if speaker in moderators else False

def convert_transcrit_to_list(transcript: List[Tag], moderators: List[str], debate_num: int) -> List[Dict[str, str]]:
    dialog_list = []
    for p in transcript:
        row = split_tag(p)
        if row == None:
            # we'll just skip non dialog rows
            continue
        row['is_moderator'] = determine_moderator(row['speaker'], moderators)
        row['debate_num'] = debate_num
        dialog_list.append(row)
    return dialog_list

def process_transcript(url: str, moderators: List[str], debate_num: int) -> List[Dict[str, str]]:
    transcript = get_tags_from_url(url)
    return  convert_transcrit_to_list(transcript, moderators, debate_num)

transcript_sources = [
    {
        'url': 'https://www.rev.com/blog/transcripts/transcript-from-first-night-of-democratic-debates',
        # moderator list source: https://www.nbcnews.com/politics/2020-election/nbc-announces-five-moderators-first-democratic-debate-n1016106
        'moderators': [
            'Lester Holt',
            'Savannah G.',
            'Chuck Todd',
            'Rachel Maddow',
            'Jose D.B.'
        ]
    },
    {
        'url': 'https://www.rev.com/blog/transcripts/transcript-from-night-2-of-the-2019-democratic-debates',
        # moderator list source: https://www.nbcnews.com/politics/2020-election/nbc-announces-five-moderators-first-democratic-debate-n1016106
        'moderators': [
            'Lester Holt',
            'Savannah G.',
            'Chuck Todd',
            'Rachel Maddow',
            'Jose D.B.'
        ]
    },
]

transcript_output = []
for i in range(len(transcript_sources)):
    src = transcript_sources[i]
    transcript = process_transcript(src['url'], src['moderators'], i + 1)
    transcript_output += transcript

print(transcript_output)
