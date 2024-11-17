import json
import os
import urllib
from collections import defaultdict
from datetime import time

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def jisho_crawler(folder="jisho_cache_", query_extra="#words #common", page_wait=1, kanji_wait=4):
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    os.makedirs(folder, exist_ok=True)

    for entry in tqdm(kanji_kyouiku):
        kanji = entry['kanji']
        # print(kanji)

        #町 #words #common

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