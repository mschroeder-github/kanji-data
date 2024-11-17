import csv
import gzip
import json
import os
import sys
import urllib
from collections import defaultdict
import time
from statistics import mean

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

import hiragana
from frequency import subtitle_freq_load
from helper import get_reading_strs
from hiragana import u_to_a
from wadoku_processing import wadoku_load


def jisho_crawler(folder="jisho_cache_", query_extra="#words #common", page_wait=1, kanji_wait=4):
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    os.makedirs(folder, exist_ok=True)

    for entry in tqdm(kanji_kyouiku):
        kanji = entry['kanji']

        search_str = urllib.parse.quote(f"{kanji} {query_extra}")

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

            time.sleep(page_wait)

        # print('wait ...')
        time.sleep(kanji_wait)

        # break


def jisho_furigana_scanner(folder="jisho_cache"):
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


def jisho_collect_common_words(folder="jisho_cache"):

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


def jisho_collect_verbs(folder="jisho_cache_verb"):

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

        kanji_kyouiku_dict = {}
        for entry in kanji_kyouiku:
            kanji_kyouiku_dict[entry['kanji']] = entry['meanings_de']

        kanji_kyouiku_reading_dict = {}
        for entry in kanji_kyouiku:
            kanji_kyouiku_reading_dict[entry['kanji']] = get_reading_strs(entry)

    freq_dict = subtitle_freq_load()

    wadoku_vocabs_dict, wadoku_vocabs_word_dict = wadoku_load()

    all_kanjis = set([entry['kanji'] for entry in kanji_kyouiku])
    all_kanjis_list = [entry['kanji'] for entry in kanji_kyouiku]

    vocabs = []
    visited_words = set()

    for filename in tqdm(os.listdir(folder)):
        path = os.path.join(folder, filename)

        with open(path, 'rt', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        title = soup.title.text

        concepts = soup.find_all("div", class_="concept_light")

        for concept in concepts:
            repr = concept.find('div', class_="concept_light-representation")
            word = repr.find('span', class_="text").get_text().strip()

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

                dan_count = { 'go': 0, 'ichi': 0 }

                # meaning
                meanings_wrapper = concept.find('div', class_="meanings-wrapper")
                meanings_wrapper_children = [child for child in meanings_wrapper.children if child.name is not None]
                meanings = []
                for i in range(0, len(meanings_wrapper_children), 2):
                    try:
                        tags = meanings_wrapper_children[i].get_text().strip()
                        meaning = meanings_wrapper_children[i + 1].find('span',
                                                                        class_="meaning-meaning").get_text().strip()

                        if 'godan verb' in tags.lower() or 'ichidan verb' in tags.lower():

                            if 'godan verb' in tags.lower():
                                dan_count['go'] += 1

                            if 'ichidan verb' in tags.lower():
                                dan_count['ichi'] += 1

                            meanings.append((meaning, tags))

                    except:
                        continue

                # only verbs with godan or ichidan
                if len(meanings) == 0:
                    continue

                reading = ''.join([r for _,r in full_word])

                kyouiku_friendly = True
                for k,c in full_word:
                    if k != c and k not in all_kanjis:
                        kyouiku_friendly = False
                        break

                max_index_list = [all_kanjis_list.index(k) for k,c in full_word if k in all_kanjis_list]
                max_index = -1
                if len(max_index_list) > 0:
                    max_index = max(max_index_list)

                if dan_count['go'] > dan_count['ichi']:
                    dan = 'go'
                elif dan_count['go'] < dan_count['ichi']:
                    dan = 'ichi'



                if dan == 'go':
                    word_neg = u_to_a(word) + 'ない'
                    reading_neg = u_to_a(reading) + 'ない'
                else:
                    word_neg = word[:-1] + 'ない'
                    reading_neg = reading[:-1] + 'ない'

                verb = {
                    'word': word,
                    'word_parts': full_word,
                    'reading': reading,
                    'dan': dan,
                    'word_neg': word_neg,
                    'reading_neg': reading_neg,
                    'meanings': meanings,
                    'meanings_de': [],
                    'kanjis': list(set(kanji for kanji in kanjis if kanji in all_kanjis)),
                    'max_kanji_index': max_index,
                    'kyouiku_friendly': kyouiku_friendly
                }

                wadoku = wadoku_vocabs_dict.get(word + reading)
                if wadoku:
                    verb['meanings_de'] = [e for w in wadoku for e in w['meanings_de']]

                # kanji meanings
                kanji_meanings_de = []
                for part in full_word:
                    if part[0] in kanji_kyouiku_dict:
                        kanji_meanings_de.append((part[0], kanji_kyouiku_dict[part[0]]))
                verb['kanji_meanings_de'] = kanji_meanings_de

                # kanji learned readings
                kanji_readings = []
                for part in full_word:
                    if part[0] in kanji_kyouiku_reading_dict:
                        kanji_readings.append((part[0], kanji_kyouiku_reading_dict[part[0]]))
                verb['kanji_readings'] = kanji_readings

                # kanji reading score
                kanji_reading_score_list = []
                for part in full_word:
                    for k, readings in kanji_readings:
                        if part[0] == k:
                            rs = [r[0] for r in readings]
                            if part[1] in rs:
                                kanji_reading_score_list.append(1)
                            else:
                                kanji_reading_score_list.append(0)

                kanji_reading_score = 0 if len(kanji_reading_score_list) == 0 else mean(kanji_reading_score_list)
                verb['kanji_reading_score'] = kanji_reading_score

                # mnemonic
                dan_decides_gender = 'Sie' if dan == 'go' else 'Er'
                hira_buffer = ''
                mnemonic_part = []
                for i, (k, c) in enumerate(full_word):
                    is_kanji = k != c

                    if not is_kanji:
                        hira_buffer += c

                    if is_kanji:
                        mnemonic_part.append(
                            f"<span class='reading kunyomi' data-hiragana='{c}' data-kanji='{k}'>{hiragana.hiragana_to_romaji(c)}</span> <span class='hiragana'>({c})</span>")

                    # buffer filled, last loop or was kanji
                    if len(hira_buffer) > 0 and (i == len(full_word) - 1 or is_kanji):
                        mnemonic_part.append(
                            f"<span class='reading hirayomi' data-hiragana='{hira_buffer}'>{hiragana.hiragana_to_romaji(hira_buffer)}</span> <span class='hiragana'>({hira_buffer})</span>")
                        hira_buffer = ''

                main_meaning_de = ''
                if len(verb['meanings_de']) > 0:
                    main_meaning_de = verb['meanings_de'][0][0]
                verb['main_meaning_de'] = main_meaning_de

                mnemonic_de = f"{dan_decides_gender} möchte {'  '.join(mnemonic_part)} {main_meaning_de}."
                verb['mnemonic_de'] = mnemonic_de
                verb['mnemonic_de_done'] = False

                # freq
                freq = {
                    'count': -1,
                    'rank': sys.maxsize,
                    'percentage': 0.0,
                    'pos': ''
                }
                freq_row = freq_dict.get(word)
                if freq_row:
                    freq['count'] = int(freq_row[1])
                    freq['rank'] = int(freq_row[4])
                    freq['percentage'] = float(freq_row[5])
                    freq['pos'] = freq_row[7]
                verb['freq'] = freq

                vocabs.append(verb)

    vocab_dict = defaultdict(list)
    for v in vocabs:
        if len(v['kanjis']) == 0:
            continue
        vocab_dict[str(v['kanjis'])].append(v)
    items = [item for item in vocab_dict.items()]
    items.sort(key=lambda x: len(x[1]), reverse=True)
    amb_count = 0
    for i in items:
        if len(i[1]) > 1:
            amb = [e['word_parts'] for e in i[1]]
            for e in i[1]:
                e['ambiguity'] = amb
            amb_count += 1

    vocabs.sort(key=lambda x: x['freq']['rank'])

    with open('../jisho_verbs.json', 'wt', encoding='utf-8') as file:
        json.dump(vocabs, file, indent=4, ensure_ascii=False)

    wadoku_avail = sum(1 for v in vocabs if len(v['meanings_de']) > 0)

    print(len(vocabs), 'verbs written,', wadoku_avail, 'wadoku available', amb_count, 'ambiguity entries')

    return vocabs


def jisho_order_verbs(lvl=50):
    with open('../jisho_verbs-wip.json', 'r', encoding='utf-8') as file:
        jisho_verbs = json.load(file)

    jisho_verbs_in = []
    jisho_verbs_out = []
    jisho_verbs_none = []
    for entry in jisho_verbs:
        if entry['max_kanji_index'] == -1:
            jisho_verbs_none.append(entry)
        elif entry['max_kanji_index'] <= lvl:
            jisho_verbs_in.append(entry)
        else:
            jisho_verbs_out.append(entry)

    jisho_verbs_in.sort(key=lambda x: x['freq']['rank'])
    jisho_verbs_out.sort(key=lambda x: x['freq']['rank'])
    jisho_verbs_none.sort(key=lambda x: x['freq']['rank'])

    jisho_verbs = jisho_verbs_in + jisho_verbs_out + jisho_verbs_none

    print(f"with level {lvl} there are {len(jisho_verbs_in)} verbs covered, {len(jisho_verbs_out)} not covered, {len(jisho_verbs_none)} none")

    with open('../jisho_verbs-wip.json', 'wt', encoding='utf-8') as file:
        json.dump(jisho_verbs, file, indent=4, ensure_ascii=False)