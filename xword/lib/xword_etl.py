import re
from datetime import date

import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError, ProgrammingError


# TODO: Add tenacity retrying.

def extract():
    formatted_date = date.strftime(date.today(), '%m/%d/%Y')
    response = requests.get('https://www.xwordinfo.com/Crossword?date={}'.format(formatted_date))
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup


def transform(response):

    title = response.h1.text
    # pattern = re.compile('New York Times')

    # # TODO: probably condense this
    # if pattern.match(title) is None:
    #     nyt, day, date, year = response.xpath(
    #         '//h3[@id="CPHContent_SubTitleH3"]/text()').extract_first().split(',')
    # else:
    #     nyt, day, date, year = title.split(',')
    #     title = ' '

    across = response.find_all(
        lambda tag: tag.has_attr('id') and tag['id'] == 'CPHContent_tdAcrossClues')[0]
    down = response.find_all(
        lambda tag: tag.has_attr('id') and tag['id'] == 'CPHContent_tdDownClues')[0]

    across_answers = [item.text for item in across.find_all('a')]
    down_answers = [item.text for item in down.find_all('a')]

    across_clues = re.split('[0-9]+\.| : ', across.text)[1::2]
    down_clues = re.split('[0-9]+\.| : ', down.text)[1::2]

    unique_words = [item.text for item in response.find_all('span', 'unique')]

    debut_words = [item.text for item in response.find_all('span', 'debut')]

    debut_words = filter(lambda x: x.upper() == x, set(unique_words).union(set(debut_words)))

    return dict(
        title=title,
        across_answers=across_answers,
        across_clues=across_clues,
        down_answers=down_answers,
        down_clues=down_clues,
        debut_words=debut_words,
    )


def load(content):
    from xword.models.xwords import Xwords
    from xword.models.sunday_titles import SundayTitles
    from app import app, db
    with app.app_context():
        title = content['title']
        across_clues = content['across_clues']
        across_answers = content['across_answers']
        down_clues = content['down_clues']
        down_answers = content['down_answers']
        debut_words = content['debut_words']

        across_objects = []
        for clue, answer in zip(across_clues, across_answers):
            debut = clue in debut_words
            across_objects.append(
                Xwords(clue=clue, answer=answer, debut=debut, orientation='across')
            )
        db.session.add_all(across_objects)

        down_objects = []
        for clue, answer in zip(down_clues, down_answers):
            debut = clue in debut_words
            down_objects.append(Xwords(clue=clue, answer=answer, debut=debut, orientation='down'))
        db.session.add_all(down_objects)

        if title:
            today = date.today()
            db.session.add(SundayTitles(title=title, date=today))

        try:
            db.session.commit()
        except (IntegrityError, ProgrammingError):
            db.session.rollback()
            raise


def verify(content):
    if isinstance(content, list):
        if len(content) > 0:
            content = content[0]
            # convert unicode to str
            return content.encode('ascii', 'ignore')
        else:
            return ""
    else:
        # convert unicode to str
        return content.encode('ascii', 'ignore')


def etl():
    response = extract()
    content = transform(response)
    load(content)
