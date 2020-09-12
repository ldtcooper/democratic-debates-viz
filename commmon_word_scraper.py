from re import template
import requests
import bs4
import json
from typing import List
Tag = bs4.element.Tag

def tag_to_list(tag: Tag) -> List[str]:
    string_list = tag.decode_contents().split('<br/>')
    return [el.strip() for el in string_list]


def get_words_from_url(url: str) -> List[str]:
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.content, 'html.parser')
    paragraphs = soup.find('div', {'class': 'field-item'}).find_all('p')
    return tag_to_list(paragraphs[1])

def save_words(words: List[str], name: str) -> None:
    text_file = open(name, 'w')
    n = text_file.write(json.dumps(words))
    text_file.close()

def get_name_from_url(url: str) -> str:
    template = '{name}.json'
    name = url.split('/')[-2]
    return template.format(name = name)

def scrape(url: str) -> None:
    words = get_words_from_url(url)
    name = get_name_from_url(url)
    save_words(words, name)
    
urls = [
    'https://www.ef.edu/english-resources/english-vocabulary/top-1000-words/',
    'https://www.ef.edu/english-resources/english-vocabulary/top-3000-words/'
]

for url in urls:
    scrape(url)

