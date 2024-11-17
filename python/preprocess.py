import random
import sys
import time
import urllib.parse

import numpy as np
from hiragana import hiragana_to_romaji, hiragana_to_ascii, u_to_a
import csv
import gzip
from collections import defaultdict
import json
import os
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup

from functools import cmp_to_key
import genanki
import glob
import pickle
import re
from collections import OrderedDict
import xml.etree.ElementTree as ET
from xml.dom import minidom


def add_german():
    '''
    Add German meanings using the kanji-trainer.org site.
    :return: Writes kanji-kyouiku-de.json
    '''

    html = requests.get('https://www.kanji-trainer.org/Merksatz/index.html')
    soup = BeautifulSoup(html.content, 'html.parser')
    table = soup.find('table')

    kanji_dict = {}

    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        #print(tds[1].getText(), tds[3].getText().split(","))
        kanji_dict[tds[1].getText().strip()] = [e.strip() for e in tds[3].getText().split(",")]

    # print(kanji_dict)

    with open('../kanji-kyouiku.json', 'rt') as file:
        kanji_kyouiku = json.load(file)

    for k, v in kanji_kyouiku.items():
        meanings_de = kanji_dict[k]

        if meanings_de is None:
            raise RuntimeError(k)

        v['meanings_de'] = meanings_de

    with open('../kanji-kyouiku-de.json', 'wt', encoding='utf-8') as file:
        json.dump(kanji_kyouiku, file, indent=4, ensure_ascii=False)


def radicals_check():
    '''
    Creates kanji-kyouiku-de-radicals.json by adding translated radical meaning information.
    See also https://www.wanikani.com/radicals
    :return:
    '''
    with open('../kanji-kyouiku-de.json', 'rt') as file:
        kanji_kyouiku = json.load(file)

    radicals = defaultdict(int)

    for k,v in kanji_kyouiku.items():
        if v['wk_radicals'] is not None:
            for rad in v['wk_radicals']:
                radicals[rad] += 1

    with open('../radical-translations.csv', 'rt') as file:
        rows = [row for row in csv.reader(file)]

    rad_set = set()
    for row in rows:
        if row[3] in rad_set:
            print(row[3], 'duplicate')
        rad_set.add(row[3])

    radical_dict = {}
    for row in rows:
        radical_dict[row[2]] = { 'kanji': row[1], 'de': row[3] }

    missing = []

    for k, v in tqdm(dict(sorted(radicals.items(), key=lambda item: item[1], reverse=True)).items()):
        print(k, v)

        if k not in radical_dict:
            missing.append(k)

    # 391 radicals
    print(len(radicals.keys()), 'radicals')
    print(len(rows), 'rows')
    print(len(missing), 'missing', missing)

    for k, v in kanji_kyouiku.items():
        wk_radicals_new = []
        wk_radicals_missing = []
        wk_radicals_de = []
        wk_radicals_kanji = []

        if v['wk_radicals'] is None:
            continue

        for rad in v['wk_radicals']:
            if rad not in radical_dict:
                wk_radicals_missing.append(rad)
            else:
                wk_radicals_new.append(rad)

                if len(radical_dict[rad]['kanji']) != 0:
                    wk_radicals_kanji.append(radical_dict[rad]['kanji'])

                wk_radicals_de.append(radical_dict[rad]['de'])

        v['wk_radicals_new'] = wk_radicals_new
        v['wk_radicals_missing'] = wk_radicals_missing
        v['wk_radicals_de'] = wk_radicals_de
        v['wk_radicals_kanji'] = wk_radicals_kanji

        no_kanji_radicals_de = set([
            "Pistole",
            "Stock",
            "Blatt",
            "Hut",
            "Triceratops",
            "Bettler",
            "Hörner",
            "Stacheln",
            "Kick",
            "Wikinger",
            "Umhang",
            "Stollen",
            "Gladiator",
            "Papst",
            "Frühling",
            "Tintenfisch",
            "Rundzelt",
            "Chinesisch"
        ])


        if len(v['wk_radicals_de']) != len(v['wk_radicals_kanji']):
            array = []
            j = 0
            for i, abc in enumerate(v['wk_radicals_de']):
                if abc in no_kanji_radicals_de:
                    array.append(" ")
                else:
                    if j < len(v['wk_radicals_kanji']):
                        array.append(v['wk_radicals_kanji'][j])
                        j += 1

            # print(k, v['wk_radicals_de'], v['wk_radicals_kanji'], array)

            v['wk_radicals_kanji'] = array

            #if len(v['wk_radicals_de']) != len(array):
            #    print('missing')

    with open('../kanji-kyouiku-de-radicals.json', 'wt', encoding='utf-8') as file:
        json.dump(kanji_kyouiku, file, indent=4, ensure_ascii=False)


def dict_to_array():
    '''
    The original kanji-kyouiku.json is a dict.
    Because of sorting it might be better if it is an array of dicts.
    :return:
    '''

    with open('../kanji-kyouiku-de-radicals.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    entries = []
    for k, v in kanji_kyouiku.items():
        v['kanji'] = k
        v['kanji_ord'] = ord(k)

        if len(v['wk_radicals_kanji']) == 1 and v['kanji'] == v['wk_radicals_kanji'][0]:
            v['is_radical'] = True
        else:
            v['is_radical'] = False

        entries.append(v)

    # sort by grade and kanji
    entries.sort(key=lambda x: (x['grade'], x['kanji_ord']))

    #entries.sort(key=lambda x: (0 if x['wk_level'] is None else x['wk_level']))
    #entries.sort(key=lambda x: len(x['wk_radicals']))

    with open('../kanji-kyouiku-de-radicals-array.json', 'wt', encoding='utf-8') as file:
        json.dump(entries, file, indent=4, ensure_ascii=False)


def prepare_mnemonics():
    '''
    We add blueprints for mnemonics.
    We have two mnemonics: meaning (radical => meaning) and reading (meaning => reading).
    :return:
    '''

    with open('../kanji-kyouiku-de-radicals-array.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    for entry in kanji_kyouiku:

        # meaning (radical => meaning)
        # make a list of radicals
        mnemonic_meaning_de = ''
        for rad_meaning, rad_kanji in zip(entry['wk_radicals_de'], entry['wk_radicals_kanji']):
            mnemonic_meaning_de += f"<span class='radical' data-kanji='{rad_kanji}'>{rad_meaning}</span> <span class='radical_kanji'>({rad_kanji})</span>  "
        # after radical we add the meaning
        mnemonic_meaning_de += f", <span class='meaning' data-kanji='{entry["kanji"]}'>{entry['meanings_de'][0]}</span> <span class='meaning_kanji_meaning'>({entry["kanji"]})</span>"

        entry['mnemonic_meaning_de'] = mnemonic_meaning_de.strip()
        entry['mnemonic_meaning_de_done'] = False

        # reading (meaning => reading)
        mnemonic_reading_de = ''
        mnemonic_reading_de += f"<span class='meaning' data-kanji='{entry["kanji"]}'>{entry['meanings_de'][0]}</span> <span class='meaning_kanji_reading'>({entry["kanji"]})</span> , "

        for wk_reading in entry['wk_readings_on']:
            if wk_reading.startswith('!') or wk_reading.startswith('^'):
                continue
            romaji = hiragana_to_romaji(wk_reading).title()
            mnemonic_reading_de += f"<span class='reading onyomi' data-hiragana='{wk_reading}'>{romaji}</span> <span class='hiragana'>({wk_reading})</span>  "

        for wk_reading in entry['wk_readings_kun']:
            if wk_reading.startswith('!') or wk_reading.startswith('^'):
                continue
            romaji = hiragana_to_romaji(wk_reading).title()
            mnemonic_reading_de += f"<span class='reading kunyomi' data-hiragana='{wk_reading}'>{romaji}</span> <span class='hiragana'>({wk_reading})</span>  "

        entry['mnemonic_reading_de'] = mnemonic_reading_de.strip()
        entry['mnemonic_reading_de_done'] = False


    with open('../kanji-kyouiku-de-radicals-array-mnemonics.json', 'wt', encoding='utf-8') as file:
        json.dump(kanji_kyouiku, file, indent=4, ensure_ascii=False)


def order_based_on_wikipedia_page():
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    # we use the order from this wiki page
    url = "https://de.wikipedia.org/wiki/Ky%C5%8Diku-Kanji"
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')

    kanji2no = {}
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 0:
            continue

        no = int(tds[0].get_text())
        kanji = tds[1].get_text()

        kanji2no[kanji] = no

        # print(no, kanji)

    # print(kanji2no)

    kanji_set = set([entry['kanji'] for entry in kanji_kyouiku])

    for entry in kanji_kyouiku:

        no = kanji2no[entry['kanji']]
        entry['order_wiki'] = no

        #if not is_done(entry):
        #    continue

        # if not is radical
        #if not entry['is_radical']:
        #    print(entry['kanji'], entry['wk_radicals_kanji'])
        #    for rad in entry['wk_radicals_kanji']:
        #        if rad not in kanji_set:
        #            print('\t', rad, 'not in set')


    kanji_kyouiku.sort(key=lambda x: x['order_wiki'])

    #for entry in kanji_kyouiku:
    #    print(entry['kanji'])

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'wt', encoding='utf-8') as file:
        json.dump(kanji_kyouiku, file, indent=4, ensure_ascii=False)

def order_based_on_radical():
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    all_kanjis = set()
    for entry in kanji_kyouiku:
        all_kanjis.add(entry['kanji'])

    kanji2entry = {}
    for entry in kanji_kyouiku:
        kanji2entry[entry['kanji']] = entry

    visited = set()

    order_wiki_radical_corrected = 1

    for entry in kanji_kyouiku:

        if entry['kanji'] in visited:
            continue

        if not entry['is_radical']:

            for rad_meaning, rad_kanji in zip(entry['wk_radicals_de'], entry['wk_radicals_kanji']):

                if rad_kanji.strip() == '':
                    rad_kanji = rad_meaning

                if rad_kanji in all_kanjis:
                    if rad_kanji not in visited:
                        kanji2entry[rad_kanji]['order_wiki_radical_corrected'] = order_wiki_radical_corrected
                        kanji2entry[rad_kanji]['grade_corrected'] = entry['grade']
                        order_wiki_radical_corrected += 1
                        visited.add(rad_kanji)

                        print(rad_kanji, ' needs to be earlier, order', kanji2entry[rad_kanji]['order_wiki_radical_corrected'], 'grade', 'std', kanji2entry[rad_kanji]['grade'], 'corrected', kanji2entry[rad_kanji]['grade_corrected'])

                else:
                    if rad_kanji not in visited:
                        # print(rad_kanji, ' is a real radical')
                        visited.add(rad_kanji)


        entry['order_wiki_radical_corrected'] = order_wiki_radical_corrected
        entry['grade_corrected'] = entry['grade']
        order_wiki_radical_corrected += 1
        visited.add(entry['kanji'])

        # print('visit', entry['kanji'], 'order', entry['order_wiki_radical_corrected'], 'grade corrected', entry['grade_corrected'])

    # sort by new order
    kanji_kyouiku.sort(key=lambda x: x['order_wiki_radical_corrected'])

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'wt', encoding='utf-8') as file:
        json.dump(kanji_kyouiku, file, indent=4, ensure_ascii=False)








