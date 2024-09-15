import random
import time
import urllib.parse

import numpy as np
from hiragana import hiragana_to_romaji, hiragana_to_ascii
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

make_anki_v2(romaji_reading=True)
make_anki_v2(romaji_reading=False)


# jisho_crawler()
# jisho_furigana_scanner()