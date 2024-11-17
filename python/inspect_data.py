import json
from collections import defaultdict

from bs4 import BeautifulSoup

from hiragana import hiragana_to_romaji


def wanikani_radicals():
    '''
    Was used to create a pasteable tab separated values to translate it to German.
    Now part of kanji-kyouiku-de-radicals.json
    :return:
    '''
    with open('../wanikani_radicals.html', 'rt', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    for section in soup.find_all('section'):

        lvl = section.find('a', { 'class': 'wk-nav__anchor'})['id'].replace('level-', '')

        for li in section.find_all('li'):

            meaning = li.find('span', { 'class': 'subject-character__meaning' }).get_text().strip()
            radical = li.find('span', { 'class': 'subject-character__characters' }).get_text().strip()

            print(lvl, radical, meaning, sep='\t')


def check_radical_kanji_mapping():
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    name2kanji = defaultdict(set)

    for entry in kanji_kyouiku:
        if len(entry['wk_radicals_de']) != len(entry['wk_radicals_kanji']):
            print(entry['wk_radicals_de'], entry['wk_radicals_kanji'])

    for entry in kanji_kyouiku:
        for (name,kanji) in zip(entry['wk_radicals_de'], entry['wk_radicals_kanji']):
            name2kanji[name].add(kanji)

    for name, kanjis in name2kanji.items():
        if len(kanjis) > 1:
            print(name, kanjis)


def reading_decision():
    data = {}

    with open('../kanji-kyouiku-de-radicals-array.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    for entry in kanji_kyouiku:
        for reading in ['wk_readings_on', 'wk_readings_kun']:
            r = entry[reading]
            if r is None:
                continue

            for yomi in entry[reading]:
                # we use wanikani feedback for the best reading (80% coverage I hope)
                if yomi.startswith('!') or yomi.startswith('^'):
                    continue

                romaji = hiragana_to_romaji(yomi)

                if romaji not in data:
                    data[romaji] = {
                        'romaji': romaji,
                        'hiragana': yomi,
                        'reading_de': [],
                        'reading_comment_de': [],
                        'wk_reading': ''
                    }


    l = list(sorted(data.values(), key=lambda x: x['romaji']))

    with open('../kanji-kyouiku-de-reading-decision.json', 'wt', encoding='utf-8') as file:
        json.dump(l, file, indent=4, ensure_ascii=False)

        
def special_radicals():
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    all_kanjis = set()
    for entry in kanji_kyouiku:
        all_kanjis.add(entry['kanji'])

    print(len(all_kanjis), 'kanji')

    special_rad = set()

    per_grade = defaultdict(set)

    for entry in kanji_kyouiku:

        #if entry['grade'] > 1:
        #    continue

        for rad, name in zip(entry['wk_radicals_kanji'], entry['wk_radicals_de']):
            if rad not in all_kanjis:
                special_rad.add((rad, name))

                per_grade[entry['grade']].add((rad, name))

    print(special_rad)
    print(len(special_rad), 'special rads')

    for v, k in per_grade.items():
        print(v, k)