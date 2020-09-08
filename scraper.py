import requests
import pandas as pd
import bs4
from typing import List, Dict
import re
import csv

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

def convert_transcrit_to_list(transcript: List[Tag], debate_num: int) -> List[Dict[str, str]]:
    dialog_list = []
    for p in transcript:
        row = split_tag(p)
        if row == None:
            # we'll just skip non dialog rows
            continue
        row['debate_num'] = debate_num
        dialog_list.append(row)
    return dialog_list

def process_transcript(url: str, debate_num: int) -> List[Dict[str, str]]:
    transcript = get_tags_from_url(url)
    return  convert_transcrit_to_list(transcript, debate_num)

def make_csv(transcripts: List[Dict[str, str]]):
    # adapted from https://stackoverflow.com/questions/3086973/how-do-i-convert-this-list-of-dictionaries-to-a-csv-file
    headers = transcripts[0].keys()
    with open('debates.csv', 'w', encoding='utf8', newline='') as output:
        dict_writer = csv.DictWriter(output, headers)
        dict_writer.writeheader()
        dict_writer.writerows(transcripts)


transcript_sources = [
    'https://www.rev.com/blog/transcripts/transcript-from-first-night-of-democratic-debates',
    'https://www.rev.com/blog/transcripts/transcript-from-night-2-of-the-2019-democratic-debates',
    'https://www.rev.com/blog/transcripts/transcript-of-july-democratic-debate-night-1-full-transcript-july-30-2019',
    'https://www.rev.com/blog/transcripts/transcript-of-july-democratic-debate-2nd-round-night-2-full-transcript-july-31-2019',
    'https://www.rev.com/blog/transcripts/democratic-debate-transcript-houston-september-12-2019',
    'https://www.rev.com/blog/transcripts/october-democratic-debate-transcript-4th-debate-from-ohio',
    'https://www.rev.com/blog/transcripts/november-democratic-debate-transcript-atlanta-debate-transcript',
    'https://www.rev.com/blog/transcripts/december-democratic-debate-transcript-sixth-debate-from-los-angeles',
    'https://www.rev.com/blog/transcripts/january-iowa-democratic-debate-transcript',
    'https://www.rev.com/blog/transcripts/new-hampshire-democratic-debate-transcript',
    'https://www.rev.com/blog/transcripts/democratic-debate-transcript-las-vegas-nevada-debate',
    'https://www.rev.com/blog/transcripts/south-carolina-democratic-debate-transcript-february-democratic-debate',
    'https://www.rev.com/blog/transcripts/march-democratic-debate-transcript-joe-biden-bernie-sanders'
]

transcript_output = []
for i in range(len(transcript_sources)):
    url = transcript_sources[i]
    transcript = process_transcript(url, i + 1)
    transcript_output += transcript

make_csv(transcript_output)


