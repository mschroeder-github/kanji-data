import random
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
import networkx as nx
from networkx import DiGraph
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from scipy.spatial.distance import cosine
from functools import cmp_to_key
import genanki
import glob
import pickle
import re

def best_reading_german_word_match():

    # all 1000 school kanjis
    with open('../kanji-kyouiku.json', 'rt') as file:
        kanji_kyouiku = json.load(file)


    # we make a dict for the yomi (does not matter for on/kun)
    yomi_dict = defaultdict(int)

    yomi2meaning = defaultdict(list)

    for kanji, data in kanji_kyouiku.items():
        # print(kanji)
        for reading in ['wk_readings_on', 'wk_readings_kun']:
            r = data[reading]
            if r is None:
                continue

            for yomi in data[reading]:
                # we use wanikani feedback for the best reading (80% coverage I hope)
                if yomi.startswith('!') or yomi.startswith('^'):
                    continue

                yomi_dict[yomi] += 1

                for meaning in data['wk_meanings']:
                    if meaning.startswith('!') or meaning.startswith('^'):
                        continue

                    yomi2meaning[yomi].append(meaning)
                # print('\t', yomi, romaji)

    with gzip.open('../dict-pos_comma.csv.gz', mode='rt', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    print(len(rows), 'rows')

    # we have 334 words because some are used for multiple meanings
    print(len(yomi_dict.keys()), ' yomi words')

    langs = ['de', 'en']
    data = {}

    # ok now we have all the word how they are read most commonly
    for k,v in tqdm(dict(sorted(yomi_dict.items(), key=lambda item: item[1], reverse=True)).items()):
        romaji = hiragana_to_romaji(k)

        ctx = {}
        ctx['hiragana'] = k
        ctx['romaji'] = romaji
        ctx['frequency'] = v

        data[romaji] = ctx

        for lang in langs:
            for mode in ['start', 'end', 'contains']:
                ctx[f'match_rows_{mode}_{lang}'] = []
                #ctx[f'langs_{mode}_{lang}'] = defaultdict(int)
                #ctx[f'pos_{mode}_{lang}'] = defaultdict(int)

        ctx['romajis'] = [romaji]

        mappings = {
            ("sh", "sch"),
            ("ou", "oo"),
            ("ou", "oh"),
            ("ou", "o"),
            ("uu", "u"),
            ("y", "i"),
            ("y", "ie"),
            ("y", "ih"),
            ("y", "ieh"),
            ("tsu", "zu"),
            ("tsu", "tze"),
            ("tsu", "TTsu"),
            ("a", "AH"),
            ("e", "EH"),
            ("i", "IH"),
            ("o", "OH"),
            ("u", "UH")
        }
        while True:
            replaced = False
            for rom in ctx['romajis']:
                for k,v in mappings:
                    if k in rom:
                        rep = rom.replace(k, v)
                        if rep not in ctx['romajis']:
                            ctx['romajis'].append(rep)
                            replaced = True
            if not replaced:
                break

        for row in rows:
            if row[2] not in langs:
                continue

            for rom in ctx['romajis']:
                for mode, condition in [
                    ('start', lambda x,y: x.startswith(y)),
                    ('end', lambda x,y: x.endswith(y)),
                    #('contains', lambda x,y: y in x)
                ]:
                    if condition(row[0].lower(), rom.lower()):
                        ctx[f'match_rows_{mode}_{row[2]}'].append(row)
                        #ctx[f'langs_{mode}_{row[2]}'][row[1]] += 1
                        #ctx[f'pos_{mode}_{row[2]}'][row[2]] += 1

        ctx['meanings'] = yomi2meaning[ctx['hiragana']]

        for lang in langs:
            for mode in ['start', 'end', 'contains']:
                # shortest first
                ctx[f'match_rows_{mode}_{lang}'].sort(key=lambda x: len(x[0]))

        count = len(ctx['match_rows_start_de'])
        if count == 0:
            count = len(ctx['match_rows_end_de'])


    with open(f'../docs/best_reading_german_word_match.js', 'wt') as file:
        file.write("const best_reading_german_word_match = \n")
        json.dump(data, file, indent=2)
        file.write(";\n")


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


def radical_graph():
    g = DiGraph()

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    for entry in kanji_kyouiku:
        #if entry['grade'] > 1:
        #    break

        g.add_node(entry['kanji'], meaning=entry['meanings_de'][0])

        for rad_meaning, rad_kanji in zip(entry['wk_radicals_de'], entry['wk_radicals_kanji']):

            if rad_kanji.strip() == '':
                rad_kanji = rad_meaning

            g.add_node(rad_kanji, meaning=rad_meaning)
            g.add_edge(rad_kanji, entry['kanji'])

    print(g.number_of_edges(), 'edges')
    print(g.number_of_nodes(), 'nodes')

    no_incoming = [(node, data) for node, data in g.nodes(data=True) if g.in_degree(node) == 0]

    # 133  no incoming nodes
    print(len(no_incoming), ' no incoming nodes')

    for node in no_incoming:
        print(node)

    #for edge in g.edges:
    #    print(edge)

    # Create hierarchical layout
    pos = graphviz_layout(g, prog="dot")

    plt.figure(figsize=(8, 6))
    # Draw the graph
    nx.draw(g, pos, with_labels=True, arrows=True, node_size=2000, node_color="lightblue", font_size=10, font_family="sans-serif")

    # Save the graph as SVG
    plt.savefig("../radical.svg", format="svg")

    nx.write_graphml(g, "../radical.graphml", encoding="utf-8")

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

def germanet_categories():

    germanet_list = defaultdict(list)
    germanet_set = defaultdict(set)

    all_categories = []

    filenames = os.listdir('../germanet')
    filenames.sort()
    # print(filenames)

    for filename in tqdm(filenames):

        category, _ = os.path.splitext(filename)

        # adj, nomen, verben might not matter
        category = category.split('.')[1]

        all_categories.append(category)

        with open(os.path.join('../germanet', filename), 'r') as file:
            soup = BeautifulSoup(file, 'xml')

        orth_forms = soup.find_all('orthForm')

        for orth in orth_forms:
            #germanet_list[orth.text.lower()].append(category)
            germanet_set[orth.text.lower()].add(category)


    print(len(all_categories), ' categories')
    print(len(germanet_list), ' germanet list entries')
    print(len(germanet_set), ' germanet set entries')

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    germanet = germanet_set

    for entry in kanji_kyouiku:
        embedding = [0.0] * len(all_categories)

        # ['Buch', 'Ursprung', 'Zählwort f. lange Dinge', 'wahr']
        # "wahr" will get 1/4
        for i, meaning in enumerate(entry['meanings_de']):
            rank = i + 1
            meaning = meaning.lower()
            for cat in germanet[meaning]:
                embedding[all_categories.index(cat)] += 1 # 1 / rank

            # only the first meaning
            break

        total = sum([e for e in embedding])
        categories = [all_categories[i] for i, e in enumerate(embedding) if e > 0]

        if total > 0:
            # normalize
            embedding = [(e / total) for e in embedding]

            germanet_dict = {
                "categories": categories,
                "embedding": embedding
            }
            entry['germanet'] = germanet_dict




    kanji_kyouiku_done = [entry for entry in kanji_kyouiku if entry['mnemonic_reading_de_done'] and 'germanet' in entry]

    print(len(kanji_kyouiku_done), 'done')

    next_index = 0

    kanji_kyouiku_sorted = []

    while kanji_kyouiku_done:
        a = kanji_kyouiku_done.pop(next_index)
        kanji_kyouiku_sorted.append(a)

        if len(kanji_kyouiku_done) == 0:
            break

        b = min(kanji_kyouiku_done, key=lambda x: cosine(a['germanet']['embedding'], x['germanet']['embedding']))

        next_index = kanji_kyouiku_done.index(b)


    for entry in kanji_kyouiku_sorted:
        print(entry['meanings_de']) #, entry['germanet']['categories'], entry['germanet']['embedding'])

def order():
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

def jisho_crawler():
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    folder = "jisho_cache_"
    os.makedirs(folder, exist_ok=True)

    for entry in tqdm(kanji_kyouiku):
        kanji = entry['kanji']
        # print(kanji)

        #町 #words #common

        search_str = urllib.parse.quote(f"{kanji} #words #common")

        for page in range(1, 100):

            path = os.path.join(folder, f"{entry['kanji_ord']}-{page}.html")

            if os.path.exists(path):
                print(path, 'exists')
                continue

            try:
                resp = requests.get('https://jisho.org/search/' + search_str + '?page=' + str(page))
            except Exception as e:
                print(e)
                continue

            if "Sorry, couldn't find anything" in resp.text:
                break

            with open(path, 'wt') as file:
                file.write(resp.text)

            time.sleep(1)

        # print('wait ...')
        time.sleep(4)

        # break

def jisho_furigana_scanner():
    folder = "jisho_cache"

    kanji2reading2num = { }

    for filename in tqdm(os.listdir(folder)):
        path = os.path.join(folder, filename)

        with open(path, 'rt', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        title = soup.title.text
        focus_kanji = title.split('#')[0].strip()

        concepts = soup.find_all("div", class_="concept_light")

        visited_word = set()
        reading2num = kanji2reading2num.get(focus_kanji)
        if reading2num is None:
            reading2num = defaultdict(int)
            kanji2reading2num[focus_kanji] = reading2num

        for concept in concepts:
            repr = concept.find('div', class_="concept_light-representation")
            word = repr.find('span', class_="text").get_text().strip()

            if word in visited_word:
                continue

            furigana = repr.find('span', class_="furigana")
            kanjis = [kanji for kanji in word]
            children = [child for child in furigana.children if child.name is not None]

            # len(kanjis) != len(children) is a special case, then they have this <ruby class="furigana-justify"><rb>歌留多</rb><rt>カルタ</rt></ruby>
            # but this happens not so often

            if len(kanjis) == len(children):

                visited_word.add(word)

                for kanji, furigana in zip(kanjis, children):
                    # print(kanji, furigana.get_text())
                    if kanji == focus_kanji:
                        reading2num[furigana.get_text()] += 1

                #print('kanji', kanji)
                #print('word', kanjis)
                #print(len(kanjis))
                #print(len(children))

                #for child in children:
                #    print('  * ', child, child.get_text())

                #print()
                #print()

        #print('focus_kanji', focus_kanji)
        #print(reading2num)
        #print()
        #break

    # print(kanji2reading2num)

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    for entry in kanji_kyouiku:
        reading2num = kanji2reading2num.get(entry['kanji'])

        if reading2num == None:
            continue

        reading2num_sorted = sorted(reading2num.items(), key=lambda item: item[1], reverse=True)

        total = sum([count for _,count in reading2num_sorted])

        reading_dist = []

        # print(reading2num_sorted)
        for reading, count in reading2num_sorted:
            reading_entry = {
                "reading": reading,
                "count": count,
                "prop": round(count / total, 2)
            }
            reading_dist.append(reading_entry)

        entry['reading_dist'] = reading_dist

        # print(json.dumps(entry, indent=2, ensure_ascii=False))

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'wt', encoding='utf-8') as file:
        json.dump(kanji_kyouiku, file, indent=4, ensure_ascii=False)


def frequency_crawler():

    links = [
        #('2013', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese/Wikipedia2013'),
        #('2013', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese10001-20000'),
        ('2015', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2015_10000'),
        ('2015', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2015_10001-20000'),
        ('2022', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2022_10000'),
        ('2022', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2022_10001-20000')
    ]

    japanese_basic_words_1000 = requests.get('https://en.m.wiktionary.org/wiki/Appendix:1000_Japanese_basic_words').content
    soup = BeautifulSoup(japanese_basic_words_1000, 'html.parser')
    japanese_basic_words_1000 = set()
    for anchor in soup.find_all('a'):
        japanese_basic_words_1000.add(anchor.get_text())

    word_dict = defaultdict(dict)

    for name, link in links:

        content = requests.get(link).content

        soup = BeautifulSoup(content, 'html.parser')

        print(link)

        tbl = soup.find('table')
        for tr in tbl.find_all('tr')[1:]:
            tds = tr.find_all('td')

            rank = int(tds[0].get_text())
            freq = int(tds[1].get_text())
            word = tds[2].get_text()

            word_dict[word][f'{name}_freq'] = freq
            word_dict[word][f'{name}_rank'] = rank
            word_dict[word][f'in_1000_basic_words'] = word in japanese_basic_words_1000

    #max_2015_rank = max([v['2015_rank'] for v in word_dict.values() if '2015_rank' in v])
    #max_2022_rank = max([v['2022_rank'] for v in word_dict.values() if '2022_rank' in v])

    min_2015_freq = min([v['2015_freq'] for v in word_dict.values() if '2015_freq' in v])
    max_2015_freq = max([v['2015_freq'] for v in word_dict.values() if '2015_freq' in v])

    min_2022_freq = min([v['2022_freq'] for v in word_dict.values() if '2022_freq' in v])
    max_2022_freq = max([v['2022_freq'] for v in word_dict.values() if '2022_freq' in v])

    # this is always 9999 (because 10,000)
    #print('max_2015_rank', max_2015_rank)
    #print('max_2022_rank', max_2022_rank)
    #print('2015 freq range', min_2015_freq, max_2015_freq)
    #print('2022 freq range', min_2022_freq, max_2022_freq)

    for v in word_dict.values():
        if '2015_rank' in v:
            v['2015_rank_prop'] = (9999 - v['2015_rank']) / 9999

        if '2022_rank' in v:
            v['2022_rank_prop'] = (9999 - v['2022_rank']) / 9999

        v['min_2015_freq'] = min_2015_freq
        v['max_2015_freq'] = max_2015_freq
        v['min_2022_freq'] = min_2022_freq
        v['max_2022_freq'] = max_2022_freq

        if '2015_freq' in v:
            v['2015_rel_freq'] = (v['2015_freq'] - min_2015_freq) / (max_2015_freq - min_2015_freq)

        if '2022_freq' in v:
            v['2022_rel_freq'] = (v['2022_freq'] - min_2022_freq) / (max_2022_freq - min_2022_freq)

    print(len(word_dict), 'in word_dict')
    print('example:', '可能', word_dict['可能'])
    print('example:', '人', word_dict['人'])

    return word_dict

def common_words_vocab_scanner():
    folder = "jisho_cache"
    pkl_file = 'vocabs.pkl'

    word_dict = frequency_crawler()

    if os.path.exists(pkl_file):
        with open(pkl_file, 'rb') as file:
            vocabs = pickle.load(file)
    else:
        vocabs = collect_vocabs()
        with open(pkl_file, 'wb') as file:
            pickle.dump(vocabs, file)

    print(len(vocabs), 'vocabs')

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    all_kanjis = set([entry['kanji'] for entry in kanji_kyouiku])

    vocabs = [vocab for vocab in vocabs if vocab['kyouiku_friendly'] and len(vocab['kanjis']) > 0]

    print(len(vocabs), 'vocabs kyouiku_friendly')

    kanji_to_reading_strs = {}

    vocab_list = []

    learned_kanjis = set()
    visited_words = set()
    for entry in tqdm(kanji_kyouiku):
        learned_kanjis.add(entry['kanji'])
        # print(learned_kanjis)

        kanji_to_reading_strs[entry['kanji']] = get_reading_strs(entry)

        for vocab in vocabs:
            if str(vocab['word_parts']) in visited_words:
                continue

            # search for vocab that has only learned kanjis in them
            intersection = vocab['kanjis'] & learned_kanjis
            contains_learned_kanjis = len(intersection) == len(vocab['kanjis'])
            if not contains_learned_kanjis:
                continue

            vocab['num_kanjis'] = len(vocab['kanjis'])
            vocab['word_len'] = len(vocab['word'])
            vocab['word_is_kanji'] = vocab['word'] in all_kanjis
            vocab['num_learned_kanjis'] = len(learned_kanjis)
            vocab['prop_learned_kanjis'] = len(learned_kanjis) / len(all_kanjis)

            # rwl = reading with learned
            rwl_total = 0
            rwl_hit = 0
            for word_part in vocab['word_parts']:
                kj = word_part[0]
                reading = word_part[1]

                reading_was_learned = False
                if kj in kanji_to_reading_strs:

                    for hira, roma in kanji_to_reading_strs[kj]:
                        if hira == reading:
                            reading_was_learned = True
                            break

                    rwl_total += 1
                    rwl_hit += 1 if reading_was_learned else 0

            vocab['rwl_hit'] = rwl_hit
            vocab['rwl_total'] = rwl_total
            vocab['rwl_prop'] = rwl_hit / rwl_total

            vocab['freq'] = word_dict.get(vocab['word'])

            # print('\tvocab:', vocab)
            vocab_list.append(vocab)
            visited_words.add(str(vocab['word_parts']))

    for vocab in vocab_list:
        vocab['kanjis'] = list(vocab['kanjis'])

    with open('../kanji-kyouiku-common-words.json', 'wt', encoding='utf-8') as file:
        json.dump(vocab_list, file, indent=4, ensure_ascii=False)

def common_words_make_anki(num_learned_kanjis=150, reading_mode="Romaji", separator=" "):

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

        kanji_kyouiku_dict = {}
        for entry in kanji_kyouiku:
            kanji_kyouiku_dict[entry['kanji']] = entry['meanings_de']

    with open('../kanji-kyouiku-common-words.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

    # emulate missing frequencies
    for word in common_words:
        if word['freq'] is None:
            word['freq'] = {
                '2015_rank': 20000,
                '2022_rank': 20000
            }

        # and set rank
        word['freq']['rank'] = word['freq'].get('2015_rank', 0) + word['freq'].get('2022_rank', 0)

    # 1. contains only learned kanjis
    # 2a. frequency is known (word['freq'] is not None)
    # 2b. has meaning
    common_words = [word for word in common_words if word['num_learned_kanjis'] <= num_learned_kanjis and len(word['meanings']) > 0]

    # 3. where I know readings
    # common_words = [word for word in common_words if word['rwl_prop'] >= 0.5]

    # 4. word is not just the kanji
    common_words = [word for word in common_words if not word['word_is_kanji']]

    # sort by rank
    common_words = sorted(common_words, key=lambda x: x['freq']['rank'])

    # print(len(common_words))

    with open('card.css', 'rt') as file:
        css = file.read().strip()

    qfmt = '''
    <span class="kanji">{{Vokabel}}</span>
    <br/>
    <br/>
    {{type:Antwort}}
    '''

    afmt = '''
    {{FrontSide}}<br/><br/>
    <div style="text-align: start;">
    {{Bedeutungen_Deutsch}}<br/>
    <br/>
    {{Bedeutungen_Englisch}}<br/>
    <br/>
    <hr/>
    <br/>
    {{Lesung_Teile}}<br/>
    <br/>
    {{Kanji_Bedeutungen}}<br/>
    <br/>
    <hr/>
    <br/>
    Rang: {{Rang}}, Lesung-Einfachheit: {{Kanji_Lesung_Gelernt}}, Kanji-Level: {{Gelernte_Kanjis_Benötigt}} 
    </div>
    '''

    deck = genanki.Deck(
        1958658640,
        'Kyōiku-Kanji Vokabeln'
    )

    model = genanki.Model(
        1518950602,
        'Kyōiku-Kanji Vokabel',
        fields=[
            {'name': 'Vokabel'},
            {'name': 'Antwort'},
            {'name': 'Bedeutungen_Deutsch'},
            {'name': 'Bedeutungen_Englisch'},
            {'name': 'Lesung_Hiragana'},
            {'name': 'Lesung_Romaji'},
            {'name': 'Lesung_Teile'},
            {'name': 'Kanji_Bedeutungen'},
            {'name': 'Kanji_Lesung_Gelernt'},
            {'name': 'Rang'},
            {'name': 'Gelernte_Kanjis_Benötigt'}
        ],
        templates=[
            {
                'name': 'Kyōiku-Kanji Vokabel Karte',
                'qfmt': qfmt,
                'afmt': afmt
            }
        ],
        css=css
    )

    count = 0
    for word in common_words:

        # not interested in numeric vocabulary
        if "'numeric'" in str(word['meanings']).lower():
            continue

        # verb check
        #for meaning in word['meanings']:
        #    m = meaning[1].lower()
        #    verb =  'godan verb' in m or 'ichidan verb' in m
            # 'suru verb' in m or
        #    if verb:
        #        print(word['word'], meaning[1], meaning[0])

        word['new_reading'] = word['rwl_prop'] < 1

        # translate
        meanings_de = []
        for meaning in word['meanings']:
            translation = translate_and_cache(meaning[0])
            meanings_de.append((translation, meaning[1]))
        word['meanings_de'] = meanings_de
        word['vocab_de'] = word['meanings_de'][0][0].split(';')[0]

        kanji_meanings_de = []
        for part in word['word_parts']:
            if part[0] in kanji_kyouiku_dict:
                kanji_meanings_de.append((part[0], kanji_kyouiku_dict[part[0]]))
        word['kanji_meanings_de'] = kanji_meanings_de

        guid = genanki.guid_for(word['word'])

        hiragana = ""
        for part in word['word_parts']:
            hiragana += part[1]
        romaji = hiragana_to_romaji(hiragana)

        vocab_de = remove_brackets(word['vocab_de'].lower()).strip()
        if len(vocab_de) == 0:
            # fallback
            vocab_de = word['vocab_de'].lower().replace('(', '').replace(')', '').strip()
            if len(vocab_de) == 0:
                raise Exception("vocab empty: " + word['vocab_de'])

        # similar to kanji: first the meaning than the reading
        answer = separator.join([vocab_de, romaji.lower().strip()])

        l = []
        for m in word['meanings_de']:
            l.append(f"{m[0]} ({m[1]})")
        meanings_de_txt = ', '.join(l)

        l = []
        for m in word['meanings']:
            l.append(f"{m[0]} ({m[1]})")
        meanings_txt = ', '.join(l)

        l = []
        for m in word['word_parts']:
            l.append(f"{m[0]}={m[1]}")
        word_parts_txt = ', '.join(l)

        l = []
        for m in word['kanji_meanings_de']:
            l.append(f"{m[0]}={';'.join(m[1])}")
        kanji_meanings_de_txt = ', '.join(l)

        note = genanki.Note(
            model=model,
            guid=guid,
            fields=[
                word['word'],
                answer,

                meanings_de_txt,
                meanings_txt,

                hiragana,
                romaji,

                word_parts_txt,
                kanji_meanings_de_txt,

                format(word['rwl_prop'], ".2f"),
                str(word['freq']['rank']),
                str(word['num_learned_kanjis'])
            ]
        )

        deck.add_note(note)

        count += 1

        #print(
        #      word['rwl_prop'],
        #      word['new_reading'],
        #      word['freq']['rank'],
        #      word['vocab_de'],
        #      word['word_parts'],
        #      word['kanji_meanings_de'],
        #      word['meanings_de']
        #)

    package = genanki.Package([deck])
    output_file = f'../anki/Kyouiku-Kanji-Vokabeln-Lvl-{num_learned_kanjis}_{reading_mode}.apkg'
    package.write_to_file(output_file)

    print(count, 'written,', 'num_learned_kanjis:', num_learned_kanjis)

def translate_and_cache(text):
    from translator import translate

    with open('../translation_cache.json', 'rt', encoding='utf-8') as file:
        translation_cache = json.load(file)

    # use cache
    if text in translation_cache:
        return translation_cache[text]

    # translate
    result = translate([text])
    translation = result[0]['translation']

    # cache
    translation_cache[text] = translation
    with open('../translation_cache.json', 'wt', encoding='utf-8') as file:
        json.dump(translation_cache, file, indent=4, ensure_ascii=False)

    return translation


def common_words_make_anki_lvls():
    max = 1050
    max = 250
    for lvl in range(50, max, 50):
        common_words_make_anki(num_learned_kanjis=lvl)

def collect_vocabs():
    folder = "jisho_cache"

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    all_kanjis = set([entry['kanji'] for entry in kanji_kyouiku])

    vocabs = []
    visited_words = set()

    for filename in tqdm(os.listdir(folder)):
        path = os.path.join(folder, filename)

        with open(path, 'rt', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        title = soup.title.text
        # focus_kanji = title.split('#')[0].strip()

        concepts = soup.find_all("div", class_="concept_light")

        # visited_word = set()
        # reading2num = kanji2reading2num.get(focus_kanji)
        # if reading2num is None:
        #    reading2num = defaultdict(int)
        #    kanji2reading2num[focus_kanji] = reading2num

        for concept in concepts:
            repr = concept.find('div', class_="concept_light-representation")
            word = repr.find('span', class_="text").get_text().strip()

            # if word in visited_word:
            #    continue

            furigana = repr.find('span', class_="furigana")
            kanjis = [kanji for kanji in word]
            children = [child for child in furigana.children if child.name is not None]

            if len(kanjis) == len(children):
                # print(concept)

                full_word = []
                for k, c in zip(kanjis, children):
                    if len(c.get_text().strip()) == 0:
                        full_word.append((k, k))
                    else:
                        full_word.append((k, c.get_text().strip()))

                if str(full_word) in visited_words:
                    continue
                visited_words.add(str(full_word))

                meanings_wrapper = concept.find('div', class_="meanings-wrapper")
                meanings_wrapper_children = [child for child in meanings_wrapper.children if child.name is not None]

                meanings = []
                for i in range(0, len(meanings_wrapper_children), 2):
                    try:
                        tags = meanings_wrapper_children[i].get_text().strip()
                        meaning = meanings_wrapper_children[i + 1].find('span',
                                                                        class_="meaning-meaning").get_text().strip()

                        if tags == 'Other forms' or tags == 'Notes':
                            continue

                        # print(word, full_word, ' -> ', tags, ' -> ', meaning)

                        meanings.append((meaning, tags))
                    except:
                        continue

                kyouiku_friendly = True
                for k,c in full_word:
                    if k != c and k not in all_kanjis:
                        kyouiku_friendly = False
                        break

                vocabs.append({
                    'word': word,
                    'word_parts': full_word,
                    'meanings': meanings,
                    'kanjis': set(kanji for kanji in kanjis if kanji in all_kanjis),
                    'kyouiku_friendly': kyouiku_friendly
                })

                a = 0
                # visited_word.add(word)

                # for kanji, furigana in zip(kanjis, children):
                # print(kanji, furigana.get_text())
                #    if kanji == focus_kanji:
                #        reading2num[furigana.get_text()] += 1

                # print('kanji', kanji)
                # print('word', kanjis)
                # print(len(kanjis))
                # print(len(children))

                # for child in children:
                #    print('  * ', child, child.get_text())

                # print()
                # print()

        # print('focus_kanji', focus_kanji)
        # print(reading2num)
        # print()
        # break

    # print(kanji2reading2num)
    return vocabs

def is_done(entry):
    return entry['mnemonic_reading_de_done'] and (entry['mnemonic_meaning_de_done'] or entry.get('has_radical_img'))


def make_anki(romaji_reading=False, separator=" ", meaning_kanji_bg="#fffee6", reading_kanji_bg="#e6fffd"):
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)


    qfmt_meaning = '''
<b>Bedeutung</b> von
<br/>
<br/>
<span class="kanji">{{Kanji}}</span>
<br/>
<br/>
{{type:Bedeutung}}
    '''

    reading_mode = "Romaji" if romaji_reading else "Hiragana"

    qfmt_reading = '''
<b>Lesung</b> von
<br/>
<br/>
<span class="kanji">{{Kanji}}</span>
<br/>
<br/>
''' + '{{type:Lesung'+ reading_mode +'}}'


    afmt_prefix = '''
    {{FrontSide}}
    '''

    afmt_postfix = '''
    <br/>
    <span class="additional additional_de">{{Bedeutung_Weitere_Deutsch}}</span><br/>
    <span class="additional additional_en">{{Bedeutung_Weitere_Englisch}}</span>
    '''

    # three models
    # * meaning -> mnemonic
    # * meaning -> image
    # * reading -> mnemonic

    mnemonic_meaning = genanki.Model(
        1869128057,
        'Kyōiku-Kanji Deutsch Bedeutung Merksatz',
        fields=[
            {'name': 'Kanji'},
            {'name': 'Bedeutung'},
            {'name': 'Bedeutung_Weitere_Deutsch'},
            {'name': 'Bedeutung_Weitere_Englisch'},
            {'name': 'Merksatz'}
        ],
        templates=[
            {
                'name': 'Bedeutung Merksatz Karte',
                'qfmt': qfmt_meaning,
                'afmt': afmt_prefix + '<br/><br/>{{Merksatz}}<br/>' + afmt_postfix,
            }
        ],
        css="""
        .card {
            text-align: center;
        }
        .meaning {
            font-weight: bold;
            border: 0px solid black;
            border-radius: 5px;
            padding: 3px;
        }
        .radical {
            font-weight: bold;
            border: 0px solid black;
            border-radius: 5px;
            padding: 3px;
            background-color: #a3ffb3;
        }
        .kanji {
            font-size: 50px;
            padding: 10px;""" +
            f"background-color: {meaning_kanji_bg};" +
        """
        }
        .additional {
            font-size: small;
        }
        .additional_en {
            color: gray;
        }
        """
    )

    image_meaning = genanki.Model(
        1801052884,
        'Kyōiku-Kanji Deutsch Bedeutung Merkbild',
        fields=[
            {'name': 'Kanji'},
            {'name': 'Bedeutung'},
            {'name': 'Bedeutung_Weitere_Deutsch'},
            {'name': 'Bedeutung_Weitere_Englisch'},
            {'name': 'Merkbild_Bedeutung'},
            {'name': 'Merkbild_Kanji'}
        ],
        templates=[
            {
                'name': 'Bedeutung Merkbild Karte',
                'qfmt': qfmt_meaning,
                'afmt': afmt_prefix + '<br/><br/><div class="img_container">{{Merkbild_Bedeutung}}{{Merkbild_Kanji}}</div>' + afmt_postfix
            }
        ],
        css="""
            .card {
                text-align: center;
                justify-content: center;
                display: flex;
            }
            .meaning {
                font-weight: bold;
                border: 0px solid black;
                border-radius: 5px;
                padding: 3px;
            }
            .radical {
                font-weight: bold;
                border: 0px solid black;
                border-radius: 5px;
                padding: 3px;
                background-color: #a3ffb3;
            }
            .kanji {
                font-size: 50px;
                padding: 10px;""" +
                f"background-color: {meaning_kanji_bg};" +
            """
            }
            .additional {
                font-size: smaller;
            }
            .additional_en {
                color: gray;
            }
            
            .img_container {
                border: 1px solid gray;
                position: relative;
                width: 300px;
                height: 300px;
            }
            .image {
                position: absolute;
                top: 0;
                left: 0;
                width: 300px;
                height: 300px;
            }
            .img_container img:nth-child(1) {
                animation: fade 6s infinite;
            }
            .img_container img:nth-child(2) {
                animation: fade2 6s infinite;
            }
            @keyframes fade {
                0%, 25%, 75%, 100% { opacity: 1; }
                50% { opacity: 0; }
            }
            @keyframes fade2 {
                0%, 100% { opacity: 0; }
                25%, 50%, 75% { opacity: 1; }
            }
            """
    )

    mnemonic_reading = genanki.Model(
        2114858346,
        'Kyōiku-Kanji Deutsch Lesung Merksatz',
        fields=[
            {'name': 'Kanji'},
            {'name': 'LesungHiragana'},
            {'name': 'LesungRomaji'},
            {'name': 'Merksatz'}
        ],
        templates=[
            {
                'name': 'Lesung Merksatz Karte',
                'qfmt': qfmt_reading,
                'afmt': '{{FrontSide}}<br/><br/>{{Merksatz}}'
            }
        ],
        css="""
            .card {
                text-align: center;
            }
            .meaning {
                font-weight: bold;
                border: 0px solid black;
                border-radius: 5px;
                padding: 3px;
            }
            .reading {
                font-weight: bold;
                border: 0px solid black;
                border-radius: 5px;
                padding: 3px;
                padding-right: 1px;
                padding-left: 1px;
            }
            .onyomi {
                background-color: #ffa3a3;
            }
            .kunyomi {
                background-color: #a3d9ff;
            }
            .kanji {
                font-size: 50px;
                padding: 10px;""" +
                f"background-color: {reading_kanji_bg};" +
            """
            }
            """
    )

    decks = []

    # main deck
    kanji_kyouiku_deck = genanki.Deck(
        2114858346,
        'Kyōiku-Kanji Deutsch')
    decks.append(kanji_kyouiku_deck)

    # Create a subdeck
    kanji_kyouiku_first_grade_deck = genanki.Deck(
        1783656266,
        'Kyōiku-Kanji Deutsch::Erstes Schuljahr')
    decks.append(kanji_kyouiku_first_grade_deck)


    for entry in kanji_kyouiku:
        if not is_done(entry):
            continue

        if entry['grade'] == 1:
            if not entry['is_radical']:
                note = genanki.Note(
                    model=mnemonic_meaning,
                    fields=[
                        entry['kanji'],
                        entry['meanings_de'][0].lower(),
                        ", ".join(entry['meanings_de']),
                        ", ".join(entry['meanings']),
                        entry['mnemonic_meaning_de']
                    ]
                )
                kanji_kyouiku_first_grade_deck.add_note(note)
            else:
                radical_name = entry['wk_radicals_de'][0]
                note = genanki.Note(
                    model=image_meaning,
                    fields=[
                        entry['kanji'],
                        entry['meanings_de'][0].lower(),
                        ", ".join(entry['meanings_de']),
                        ", ".join(entry['meanings']),
                        f'<img class="image" src="{radical_name}-img.jpg">',
                        f'<img class="image" src="{radical_name}-kanji.png">'
                    ]
                )
                kanji_kyouiku_first_grade_deck.add_note(note)

            # turn reading mnemonic to reading check
            reading_strs = get_reading_strs(entry)

            reading_hiragana = separator.join([r[0] for r in reading_strs])
            reading_romaji = separator.join([r[1] for r in reading_strs])

            note = genanki.Note(
                model=mnemonic_reading,
                fields=[
                    entry['kanji'],
                    reading_hiragana,
                    reading_romaji,
                    entry['mnemonic_reading_de']
                ]
            )
            kanji_kyouiku_first_grade_deck.add_note(note)


    # export package
    package = genanki.Package(decks)
    package.media_files = []
    package.media_files.extend(glob.glob('../img/*.jpg'))
    package.media_files.extend(glob.glob('../img/*.png'))

    output_file = f'../anki/Kyouiku-Kanji-Deutsch_{reading_mode}.apkg'
    package.write_to_file(output_file)


def make_anki_v2(romaji_reading=False, separator=" "):
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    with open('card.css', 'rt') as file:
        css = file.read().strip()

    qfmt_default = '''
<span class="kanji">{{Kanji}}</span>
<br/>
<br/>
{{type:Antwort}}
    '''

    afmt_postfix = '''
    <br/>
    <br/>
    <span class="additional additional_de">{{Bedeutung_Weitere_Deutsch}}</span><br/>
    <span class="additional additional_en">{{Bedeutung_Weitere_Englisch}}</span>
    '''

    afmt_mnemonic = ('{{FrontSide}}' +
                     '<br/><br/>{{Merksatz_Bedeutung}}<br/><br/>{{Merksatz_Lesung}}' +
                     afmt_postfix)

    afmt_image = ('{{FrontSide}}' +
                  '<br/><br/>{{Merksatz_Lesung}}<br/><br/><div class="img_container">{{Merkbild_Bedeutung}}{{Merkbild_Kanji}}</div>' +
                  afmt_postfix)

    # two models
    # * meaning, reading -> mnemonic, mnemonic
    # * meaning, reading -> image

    mnemonic_meaning = genanki.Model(
        1695632296,
        'Kyōiku-Kanji Deutsch Bedeutung/Lesung Merksatz',
        fields=[
            {'name': 'Kanji'},
            {'name': 'Antwort'},
            {'name': 'Bedeutung'},
            {'name': 'Bedeutung_Weitere_Deutsch'},
            {'name': 'Bedeutung_Weitere_Englisch'},
            {'name': 'Merksatz_Bedeutung'},
            {'name': 'Lesung_Hiragana'},
            {'name': 'Lesung_Romaji'},
            {'name': 'Merksatz_Lesung'}
        ],
        templates=[
            {
                'name': 'Bedeutung/Lesung Merksatz Karte',
                'qfmt': qfmt_default,
                'afmt': afmt_mnemonic
            }
        ],
        css=css
    )

    image_meaning = genanki.Model(
        1835909438,
        'Kyōiku-Kanji Deutsch Bedeutung/Lesung Merkbild',
        fields=[
            {'name': 'Kanji'},
            {'name': 'Antwort'},
            {'name': 'Bedeutung'},
            {'name': 'Bedeutung_Weitere_Deutsch'},
            {'name': 'Bedeutung_Weitere_Englisch'},
            {'name': 'Merkbild_Bedeutung'},
            {'name': 'Merkbild_Kanji'},
            {'name': 'Lesung_Hiragana'},
            {'name': 'Lesung_Romaji'},
            {'name': 'Merksatz_Lesung'}
        ],
        templates=[
            {
                'name': 'Bedeutung/Lesung Merkbild Karte',
                'qfmt': qfmt_default,
                'afmt': afmt_image
            }
        ],
        css=css
    )

    decks = []

    # main deck
    kanji_kyouiku_deck = genanki.Deck(
        1818403339,
        'Kyōiku-Kanji Deutsch')
    decks.append(kanji_kyouiku_deck)

    # Create a subdeck
    #no2deck = { }
    #no2deck['1'] = genanki.Deck(
    #    1519507022,
    #    'Kyōiku-Kanji Deutsch::1. Schuljahr')
    #no2deck['2'] = genanki.Deck(
    #    2002120349,
    #    'Kyōiku-Kanji Deutsch::2. Schuljahr')
    #no2deck['3'] = genanki.Deck(
    #    1621021171,
    #    'Kyōiku-Kanji Deutsch::3. Schuljahr')
    #no2deck['4'] = genanki.Deck(
    #    1298392758,
    #    'Kyōiku-Kanji Deutsch::4. Schuljahr')
    #no2deck['5'] = genanki.Deck(
    #    1670745543,
    #    'Kyōiku-Kanji Deutsch::5. Schuljahr')
    #no2deck['6'] = genanki.Deck(
    #    1555589751,
    #    'Kyōiku-Kanji Deutsch::6. Schuljahr')

    #no2total = defaultdict(int)

    actual = 0
    for entry in kanji_kyouiku:
        #no2total[str(entry['grade'])] += 1

        if not is_done(entry):
            continue

        actual += 1

        # turn reading mnemonic to reading check
        reading_strs = get_reading_strs(entry)

        reading_hiragana = separator.join([r[0] for r in reading_strs])
        reading_romaji = separator.join([r[1] for r in reading_strs])
        reading_answer = reading_romaji if romaji_reading else reading_hiragana

        answer = separator.join([entry['meanings_de'][0].lower(), reading_answer])

        kanji_guid = genanki.guid_for(entry['kanji'])

        if not entry['is_radical']:
            note = genanki.Note(
                model=mnemonic_meaning,
                guid=kanji_guid,
                fields=[
                    entry['kanji'],
                    answer,
                    entry['meanings_de'][0].lower(),
                    ", ".join(entry['meanings_de']),
                    ", ".join(entry['meanings']),
                    entry['mnemonic_meaning_de'],
                    reading_hiragana,
                    reading_romaji,
                    entry['mnemonic_reading_de']
                ]
            )

        else:
            radical_name = entry['wk_radicals_de'][0]
            note = genanki.Note(
                model=image_meaning,
                guid=kanji_guid,
                fields=[
                    entry['kanji'],
                    answer,
                    entry['meanings_de'][0].lower(),
                    ", ".join(entry['meanings_de']),
                    ", ".join(entry['meanings']),
                    f'<img class="image" src="{radical_name}-img.jpg">',
                    f'<img class="image" src="{radical_name}-kanji.png">',
                    reading_hiragana,
                    reading_romaji,
                    entry['mnemonic_reading_de']
                ]
            )

        # no2deck[str(entry['grade'])].add_note(note)
        kanji_kyouiku_deck.add_note(note)

    #for no, deck in no2deck.items():
    #    if len(deck.notes) > 0:
    #        decks.append(deck)

    # export package
    package = genanki.Package(decks)
    package.media_files = []
    package.media_files.extend(glob.glob('../img/*.jpg'))
    package.media_files.extend(glob.glob('../img/*.png'))

    reading_mode = "Romaji" if romaji_reading else "Hiragana"
    output_file = f'../anki/Kyouiku-Kanji-Deutsch_{reading_mode}.apkg'
    package.write_to_file(output_file)

    #actual_sum = 0
    #expected_sum = 0
    #text = ""
    #for no in sorted(no2total.keys()):
    #    actual = len(no2deck[no].notes)
    #    expected = no2total[no]
    #    actual_sum += actual
    #    expected_sum += expected
    #    percent = int((actual / expected) * 100)
    #    text += f"{no}. grade: {actual: 5} /{expected: 5} {percent: 4}%\n"

    total = len(kanji_kyouiku)
    percent_total = int((actual / total) * 100)
    print(f"total: {actual: 5} /{total: 5} {percent_total: 4}%")
    # print("---------------------------")
    print()


def get_reading_strs(entry):
    soup = BeautifulSoup(entry['mnemonic_reading_de'], 'html.parser')
    readings = soup.find_all("span", class_="reading")
    reading_strs = []
    for r in readings:
        hiragana = r['data-hiragana']
        romaji = hiragana_to_romaji(hiragana)
        reading_strs.append((hiragana, romaji))
    return reading_strs

def remove_brackets(text):
    return re.sub(r'\(.*?\)', '', text)


def extract_kanji(text):
    kanji_pattern = r'[\u4e00-\u9faf]'
    kanji_characters = re.findall(kanji_pattern, text)
    return list(set(kanji_characters))

def verbs_scanner():
    with open('../kanji-kyouiku-common-words.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

        common_words_dict = defaultdict(list)

        # emulate missing frequencies
        for word in common_words:
            if word['freq'] is None:
                word['freq'] = {
                    '2015_rank': 20000,
                    '2022_rank': 20000
                }

            # and set rank
            word['freq']['rank'] = word['freq'].get('2015_rank', 0) + word['freq'].get('2022_rank', 0)

            common_words_dict[word['word']].append(word)

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

        kanji_kyouiku_dict = {}
        kanji_kyouiku_list = []

        for entry in kanji_kyouiku:
            kanji_kyouiku_dict[entry['kanji']] = {
                'meanings_de': entry['meanings_de'],
                'reading_dist': entry.get('reading_dist'),
                'reading_strs': get_reading_strs(entry)
            }

            kanji_kyouiku_list.append(entry['kanji'])

    html = requests.get('https://www.japaneseverbconjugator.com/JVerbList.asp')
    soup = BeautifulSoup(html.content, 'html.parser')

    table = soup.find_all('table')[1]

    kyouiku_verbs = []

    error_count = 0

    i = 1
    easy_count = 0
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')

        if len(tds) < 4:
            continue

        romaji = tds[0].get_text().strip()

        furigana = tds[1].find('span', class_="furigana").get_text().strip()
        kanji_text_elem = tds[1].find('div', class_="JScript")

        if kanji_text_elem is None:
            error_count += 1
            continue

        kanji_text = kanji_text_elem.get_text().strip()

        if len(kanji_text) == 0 or len(furigana) == 0:
            error_count += 1
            continue

        meaning = tds[2].get_text().strip()

        #ms = []
        #for m in meaning.split(','):
        #    m = m.strip()
        #    m_de = translate_and_cache(m)
        #    ms.append(m_de)
        # meaning_de = ', '.join(ms)

        meaning_de = translate_and_cache(meaning)
        mode = tds[3].get_text().strip()

        # fix
        if kanji_text == '加わる':
            # Godan, see https://jisho.org/search/%E5%8A%A0%E3%82%8F%E3%82%8B
            mode = '1'

        # need negative plain form for correct conjugation later
        if mode == '1':
            # Godan
            kanji_text_neg = u_to_a(kanji_text) + 'ない'
            furigana_neg = u_to_a(furigana) + 'ない'

        elif mode == '2':
            # Ichidan
            kanji_text_neg = kanji_text[:-1] + 'ない'
            furigana_neg = furigana[:-1] + 'ない'

        else:
            raise Exception("mode not found: " + mode + ", " + kanji_text)

        #better kanji detection
        extracted_kanjis = extract_kanji(kanji_text)
        kyouiku_kanjis = []
        reading_learned = False
        for char in extracted_kanjis:
            if char in kanji_kyouiku_dict:
                readings = kanji_kyouiku_dict[char]['reading_strs']
                kyouiku_kanjis.append((char, kanji_kyouiku_dict[char]['meanings_de'], readings))
                for hira, roma in readings:
                    reading_learned |= furigana.startswith(hira)

        matching_words = common_words_dict.get(kanji_text, [])

        kyouiku_friendly = len(extracted_kanjis) > 0 and len(extracted_kanjis) == len(kyouiku_kanjis)

        kyouiku_index = -1
        if kyouiku_friendly:
            kyouiku_index = kanji_kyouiku_list.index(kyouiku_kanjis[0][0])

        # 422 having all info
        # 249 with a match
        #  12 with two   or more matches
        #   0 with three or more matches
        #  13 have two kanjis
        #  78 reading is learned (and kyouiku_friendly), can be higher later
        # 280 kyouiku_friendly (66%, 2/3)


        #if kyouiku_friendly and reading_learned:
        # if len(matching_words) > 0:
        if kyouiku_friendly:
            easy_count += 1

        kyouiku_verb = {
            'romaji': romaji,
            'furigana': furigana,
            'furigana_neg': furigana_neg,
            'word': kanji_text,
            'word_neg': kanji_text_neg,
            'kanjis': kyouiku_kanjis,
            'kyouiku_index': kyouiku_index,
            'meaning': meaning,
            'meaning_de': meaning_de,
            'mode': mode,
            'kyouiku_friendly': kyouiku_friendly,
            'reading_learned': reading_learned,
            'common_words': matching_words
        }
        kyouiku_verbs.append(kyouiku_verb)

        #print(i, romaji, furigana, kanji_text, kanjis, meaning, meaning_de, mode, kyouiku_friendly, reading_learned, len(matching_words), kyouiku_index, sep=' | ')
        #for word in matching_words:
        #    print('\t', word)
        #i += 1

    #print(easy_count)

    # 108
    # print(error_count)

    kyouiku_verbs.sort(key=lambda x: (len(x['kanjis']), x['kyouiku_index']))

    #print(len(kyouiku_verbs))

    with open('card.css', 'rt') as file:
        css = file.read().strip()

    qfmt = '''
    <span class="kanji">{{Vokabel}}</span>
    <br/>
    <br/>
    {{type:Antwort}}
    '''

    afmt = '''
    {{FrontSide}}<br/>
    <br/>
    <div style="text-align: start;">
    {{Lesung_Hiragana}} - {{Lesung_Hiragana_Negation}}<br/>
    {{Lesung_Romaji}} - {{Lesung_Romaji_Negation}}<br/>
    <br/>
    {{Bedeutungen_Deutsch}}<br/>
    <br/>
    {{Bedeutungen_Englisch}}<br/>
    <br/>
    <hr/>
    <br/>
    {{Kanji_Bedeutungen}}<br/>
    <br/>
    <hr/>
    <br/>
    Typ: {{Dan}}-Dan, Lesung-Einfachheit: {{Kanji_Lesung_Gelernt}}, Kanji-Level: {{Gelernte_Kanjis_Benötigt}} 
    </div>
    '''

    deck = genanki.Deck(
        1210461573,
        'Kyōiku-Kanji Verben'
    )

    model = genanki.Model(
        1417794174,
        'Kyōiku-Kanji Verb',
        fields=[
            {'name': 'Vokabel'},
            {'name': 'Antwort'},

            {'name': 'Bedeutungen_Deutsch'},
            {'name': 'Bedeutungen_Englisch'},
            {'name': 'Vokabel_Negation'},

            {'name': 'Lesung_Hiragana'},
            {'name': 'Lesung_Romaji'},
            {'name': 'Lesung_Hiragana_Negation'},
            {'name': 'Lesung_Romaji_Negation'},
            {'name': 'Kanji_Bedeutungen'},

            {'name': 'Dan'},
            {'name': 'Kanji_Lesung_Gelernt'},
            {'name': 'Gelernte_Kanjis_Benötigt'}
        ],
        templates=[
            {
                'name': 'Kyōiku-Kanji Verb Karte',
                'qfmt': qfmt,
                'afmt': afmt
            }
        ],
        css=css
    )

    i = 0
    for verb in kyouiku_verbs:
        if not verb['kyouiku_friendly']:
            continue

        # print(verb)

        guid = genanki.guid_for(verb['word'] + verb['furigana'])

        hiragana = verb['furigana']
        romaji = hiragana_to_romaji(verb['furigana'])
        romaji_neg = hiragana_to_romaji(verb['furigana_neg'])

        meanings_de_txt = verb['meaning_de'].lower()
        meanings_txt = verb['meaning'].lower()

        answer = f"{verb['meaning_de'].split(',')[0].strip()} {romaji_neg}".lower()

        l = []
        for m in verb['kanjis']:
            l.append(f"{m[0]}={';'.join(m[1])}")
        kanji_meanings_de_txt = ', '.join(l)

        note = genanki.Note(
            model=model,
            guid=guid,
            fields=[
                verb['word'],
                answer,

                meanings_de_txt,
                meanings_txt,
                verb['word_neg'],

                verb['furigana'],
                romaji,

                verb['furigana_neg'],
                romaji_neg,

                kanji_meanings_de_txt,

                'Go' if verb['mode'] == '1' else 'Ichi',
                'Ja' if verb['reading_learned'] else 'Nein',
                str(verb['kyouiku_index'])
            ]
        )

        deck.add_note(note)
        i += 1

        # print(verb)

    package = genanki.Package([deck])
    output_file = f'../anki/Kyouiku-Kanji-Verben.apkg'
    package.write_to_file(output_file)

    print(i, 'written')


# add_german()
# radicals_check()
# dict_to_array()
# prepare_mnemonics()
# check_radical_kanji_mapping()
# reading_decision()
# best_reading_german_word_match()
# radical_graph()
# special_radicals()
# germanet_categories()
# order()
# order_based_on_radical() # can be called again

# make_anki_v2(romaji_reading=True)
# make_anki_v2(romaji_reading=False)

# common_words_make_anki_lvls()

# jisho_crawler()
# jisho_furigana_scanner()


# frequency_crawler()
# common_words_vocab_scanner()

verbs_scanner()
