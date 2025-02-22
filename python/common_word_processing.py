import csv
import datetime
import gzip
import json
import os
import pickle
import sys
import time
from collections import defaultdict
import random
from string import Template

import genanki
import numpy as np
from charset_normalizer.utils import is_hiragana, is_katakana
from openai import OpenAI
from tqdm import tqdm

from deepl_api import translate_ja_de, translate_de_ja
from frequency import frequency_crawler
from helper import get_reading_strs, remove_brackets
from hiragana import hiragana_to_romaji, KYOUIKU_STR, JOYO_STR
from img_gen import generate_image
from jisho_processing import jisho_collect_common_words
from settings import BASE_URL, API_KEY, MODEL
from tts import text_to_speech
from wadoku_processing import wadoku_load

import statistics

import re

client = OpenAI(
    base_url=BASE_URL,
    api_key=API_KEY
)
codeBlockPattern = re.compile(r'(```(\w+)?\s(.*?)\s*?```)', re.DOTALL)


def common_words_vocab_scanner():
    pkl_file = 'vocabs.pkl'

    word_dict = frequency_crawler()

    if os.path.exists(pkl_file):
        with open(pkl_file, 'rb') as file:
            vocabs = pickle.load(file)
    else:
        vocabs = jisho_collect_common_words()
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

def common_words_make_anki(num_learned_kanjis=150, reading_mode="Umschrift", separator=" "):
    os.makedirs('../anki', exist_ok=True)

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

        kanji_kyouiku_dict = {}
        for entry in kanji_kyouiku:
            kanji_kyouiku_dict[entry['kanji']] = entry['meanings_de']

    with open('../kanji-kyouiku-common-words.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

        common_words_dict = {}
        for entry in common_words:
            common_words_dict[entry['word']] = entry

    wadoku_vocabs_dict, wadoku_vocabs_word_dict = wadoku_load()

    # emulate missing frequencies
    for word in common_words:
        if word['freq'] is None:
            word['freq'] = {
                '2015_rank': 20000,
                '2022_rank': 20000
            }

        # and set rank
        word['freq']['rank'] = word['freq'].get('2015_rank', 0) + word['freq'].get('2022_rank', 0)

    # subtitle based frequency
    with gzip.open('../word_freq_report.txt.gz', 'rt', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for no, row in enumerate(reader, start=1):
            row.insert(0, no)

            common_word = common_words_dict.get(row[2])
            if common_word:
                common_word['freq']['subtitle'] = row

    # emulate missing subtitle frequencies
    for word in common_words:
        if word['freq'].get('subtitle') is None:
            word['freq']['subtitle'] = [sys.maxsize, -1]

    # 1. contains only learned kanjis
    # 2a. frequency is known (word['freq'] is not None)
    # 2b. has meaning
    common_words = [word for word in common_words if word['num_learned_kanjis'] <= num_learned_kanjis and len(word['meanings']) > 0]

    # 3. where I know readings
    # common_words = [word for word in common_words if word['rwl_prop'] >= 0.5]

    # 4. word is not just the kanji
    common_words = [word for word in common_words if not word['word_is_kanji']]

    # sort by rank
    # this came from jp wikipedia
    # common_words = sorted(common_words, key=lambda x: x['freq']['rank'])
    # this came from subtitles, [0] is rank, [1] Number of times word was encountered
    common_words = sorted(common_words, key=lambda x: x['freq']['subtitle'][0])

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
    <span class="kanji">{{Vokabel}}</span>
    <br/>
    <span class="lesung_hiragana">{{Lesung_Hiragana}}</span>
    <br/>
    <br/>
    {{type:Antwort}}
    <div style="text-align: start;">
    <ul>{{Bedeutungen_Deutsch}}</ul>
    <ul>{{Bedeutungen_Englisch}}</ul>
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
        'Unterrichtsschriftzeichen - Gebräuchliche Wörter'
    )

    model = genanki.Model(
        1518950602,
        'Vokabel',
        fields=[
            {'name': 'Vokabel'}, # 0
            {'name': 'Antwort'}, # 1
            {'name': 'Bedeutungen_Deutsch'}, # 2
            {'name': 'Bedeutungen_Englisch'}, # 3
            {'name': 'Lesung_Hiragana'}, # 4
            {'name': 'Lesung_Romaji'}, # 5
            {'name': 'Lesung_Teile'}, # 6
            {'name': 'Kanji_Bedeutungen'}, # 7
            {'name': 'Kanji_Lesung_Gelernt'}, # 8
            {'name': 'Rang'}, # 9
            {'name': 'Gelernte_Kanjis_Benötigt'} # 10
        ],
        templates=[
            {
                'name': 'Kyōiku-Kanji Vokabel Karte',
                'qfmt': qfmt,
                'afmt': afmt
            }
        ],
        css=css,
        sort_field_index=9
    )

    equal_word_set = set()
    duplicate_words = []
    filtered_verbs = []
    word_freq = defaultdict(int)

    for word in common_words:
        word_freq[word['word']] += 1

    common_words = [word for word in common_words if word_freq[word['word']] <= 1]

    count = 0
    wadoku_not_found_count = 0
    for word in common_words:

        # not interested in numeric vocabulary
        if "'numeric'" in str(word['meanings']).lower():
            continue

        #if word['word'] in kyouiku_verbs_dict:
        #    filtered_verbs.append(word)
        #    continue

        # verb check
        skip_verb = False
        for meaning in word['meanings']:
            m = meaning[1].lower()
            verb = 'godan verb' in m or 'ichidan verb' in m
            # 'suru verb' in m or
            if verb:
                # print(word['word'], meaning[1], meaning[0])
                skip_verb = True
        if skip_verb:
            filtered_verbs.append(word)
            continue


        word['new_reading'] = word['rwl_prop'] < 1

        kanji_meanings_de = []
        for part in word['word_parts']:
            if part[0] in kanji_kyouiku_dict:
                kanji_meanings_de.append((part[0], kanji_kyouiku_dict[part[0]]))
        word['kanji_meanings_de'] = kanji_meanings_de

        guid = genanki.guid_for(word['word'])

        hiragana = ""
        for part in word['word_parts']:
            part_romaji = hiragana_to_romaji(part[1])
            if part[1] in kanji_kyouiku_dict:
                print(f'[WARN] {word['word']} {word['word_parts']}, kanji detected in reading: {part[1]}')
            hiragana += part[1]
        romaji = hiragana_to_romaji(hiragana)

        # translate
        meanings_de = []

        wadoku_entry_list = wadoku_vocabs_dict.get(word['word'] + hiragana)
        if wadoku_entry_list is None:
            wadoku_entry_list = wadoku_vocabs_word_dict.get(word['word'])
            if wadoku_entry_list is None:
                #raise Exception('no wadoku entry for ' + word['word'])
                # print('[WARN] no wadoku entry for ' + word['word'])
                wadoku_not_found_count += 1

                #TODO maybe later fallback translate
                continue
                #for meaning in word['meanings']:
                #    translation = translate_and_cache(meaning[0])
                #    meanings_de.append((translation, meaning[1]))


        if len(wadoku_entry_list) == 1:
            word['meanings_de'] = wadoku_entry_list[0]['meanings_de']
        else:
            word['meanings_de'] = []
            wadoku_entry_list.sort(key=lambda x: sum(len(m) for m in x['meanings_de']), reverse=True)
            for entry in wadoku_entry_list:
                word['meanings_de'].extend(entry['meanings_de'])


        # word['meanings_de'] = meanings_de
        #word['vocab_de'] = word['meanings_de'][0][0].split(';')[0]
        word['vocab_de'] = word['meanings_de'][0][0]

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
            l.append(f"<li>{'; '.join(m)}</li>")
        meanings_de_txt = '\n'.join(l)

        l = []
        for m in word['meanings']:
            l.append(f"<li>{m[0]} ({m[1]})</li>")
        meanings_txt = '\n'.join(l)

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
                str(word['freq']['subtitle'][0]), # rank
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
    output_file = f'../anki/Unterrichtsschriftzeichen_Gebraeuchliche_Woerter-Level_{num_learned_kanjis:04}-{reading_mode}_Abfrage.apkg'
    package.write_to_file(output_file)

    print(count, 'written,', 'num_learned_kanjis:', num_learned_kanjis, 'filtered_verbs:', len(filtered_verbs), 'wadoku_not_found_count:', wadoku_not_found_count)

    return common_words

def common_words_make_anki_lvls(max=50, debug_new_words=False):
    last_common_words = []
    for lvl in range(50, max+1, 50):
        common_words = common_words_make_anki(num_learned_kanjis=lvl)

        if debug_new_words:
            new_words = set([w['word'] for w in common_words]) - set([w['word'] for w in last_common_words])
            print(len(new_words), 'new words')

            d = dict((w['word'], w) for w in common_words)

            ranked_words = [(w, d[w]['freq']['rank']) for w in new_words]
            ranked_words.sort(key=lambda x: x[1])

            for rw in ranked_words:
                print('\t' + str(rw))
            print()
            print('==========================')
            print()

            last_common_words = common_words

def common_words_make_word_lists(num_learned_kanjis=150, reading_mode="Umschrift", separator=" ", include_word_is_kanji=False, simple_word_freq_fix=True):
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

        kanji_kyouiku_dict = {}
        for entry in kanji_kyouiku:
            kanji_kyouiku_dict[entry['kanji']] = entry['meanings_de']

    with open('../kanji-kyouiku-common-words.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

        common_words_dict = {}
        for entry in common_words:
            common_words_dict[entry['word']] = entry

    wadoku_vocabs_dict, wadoku_vocabs_word_dict = wadoku_load()

    # emulate missing frequencies
    for word in common_words:
        if word['freq'] is None:
            word['freq'] = {
                '2015_rank': 20000,
                '2022_rank': 20000
            }

        # and set rank
        word['freq']['rank'] = word['freq'].get('2015_rank', 0) + word['freq'].get('2022_rank', 0)

    # subtitle based frequency
    with gzip.open('../word_freq_report.txt.gz', 'rt', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for no, row in enumerate(reader, start=1):
            row.insert(0, no)

            common_word = common_words_dict.get(row[2])
            if common_word:
                common_word['freq']['subtitle'] = row

    # emulate missing subtitle frequencies
    for word in common_words:
        if word['freq'].get('subtitle') is None:
            word['freq']['subtitle'] = [sys.maxsize, -1]

    # 1. contains only learned kanjis
    # 2a. frequency is known (word['freq'] is not None)
    # 2b. has meaning
    common_words = [word for word in common_words if word['num_learned_kanjis'] <= num_learned_kanjis and len(word['meanings']) > 0]

    # 3. where I know readings
    # common_words = [word for word in common_words if word['rwl_prop'] >= 0.5]

    # 4. word is not just the kanji
    if not include_word_is_kanji:
        common_words = [word for word in common_words if not word['word_is_kanji']]

    # sort by rank
    # this came from jp wikipedia
    # common_words = sorted(common_words, key=lambda x: x['freq']['rank'])
    # this came from subtitles, [0] is rank, [1] Number of times word was encountered
    common_words = sorted(common_words, key=lambda x: x['freq']['subtitle'][0])

    equal_word_set = set()
    duplicate_words = []
    filtered_verbs = []
    word_freq = defaultdict(int)

    for word in common_words:
        word_freq[word['word']] += 1

    word_dict = defaultdict(list)
    for word in common_words:
        word_dict[word['word']].append(word)

    # freq of the word
    if simple_word_freq_fix:
        common_words = [word for word in common_words if word_freq[word['word']] <= 1]
    else:
        # we merge multi entries into one so that word exits exactly once
        ls = []
        for k, v in word_dict.items():
            if len(v) > 1:
                repr = v[0]
                for i, other in enumerate(v[1:]):
                    repr['meanings'].extend(other['meanings'])

                    if 'meanings_de' in repr:
                        repr['meanings_de'].extend(other['meanings_de'])

                    repr[f'word_parts_{i}']= other['word_parts']

                repr['is_merged'] = True
                ls.append(repr)
            else:
                ls.append(v[0])
        common_words = ls

    word_list = []

    count = 0
    wadoku_not_found_count = 0
    for word in common_words:

        # not interested in numeric vocabulary
        if "'numeric'" in str(word['meanings']).lower():
            continue

        # verb check
        skip_verb = False
        for meaning in word['meanings']:
            m = meaning[1].lower()
            verb = 'godan verb' in m or 'ichidan verb' in m
            # 'suru verb' in m or
            if verb:
                # print(word['word'], meaning[1], meaning[0])
                skip_verb = True
        if skip_verb:
            filtered_verbs.append(word)
            continue

        word['new_reading'] = word['rwl_prop'] < 1

        kanji_meanings_de = []
        for part in word['word_parts']:
            if part[0] in kanji_kyouiku_dict:
                kanji_meanings_de.append((part[0], kanji_kyouiku_dict[part[0]]))
        word['kanji_meanings_de'] = kanji_meanings_de

        guid = genanki.guid_for(word['word'])

        hiragana = ""
        for part in word['word_parts']:
            part_romaji = hiragana_to_romaji(part[1])
            if part[1] in kanji_kyouiku_dict:
                print(f'[WARN] {word['word']} {word['word_parts']}, kanji detected in reading: {part[1]}')
            hiragana += part[1]
        romaji = hiragana_to_romaji(hiragana)

        word['hiragana'] = hiragana

        # translate
        meanings_de = []

        wadoku_entry_list = wadoku_vocabs_dict.get(word['word'] + hiragana)
        if wadoku_entry_list is None:
            wadoku_entry_list = wadoku_vocabs_word_dict.get(word['word'])
            if wadoku_entry_list is None:
                # raise Exception('no wadoku entry for ' + word['word'])
                # print('[WARN] no wadoku entry for ' + word['word'])
                wadoku_not_found_count += 1

                continue

        if len(wadoku_entry_list) == 1:
            word['meanings_de'] = wadoku_entry_list[0]['meanings_de']
        else:
            word['meanings_de'] = []
            wadoku_entry_list.sort(key=lambda x: sum(len(m) for m in x['meanings_de']), reverse=True)
            for entry in wadoku_entry_list:
                word['meanings_de'].extend(entry['meanings_de'])

        # word['meanings_de'] = meanings_de
        # word['vocab_de'] = word['meanings_de'][0][0].split(';')[0]
        word['vocab_de'] = word['meanings_de'][0][0]

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
            l.append(f"<li>{'; '.join(m)}</li>")
        meanings_de_txt = '\n'.join(l)

        l = []
        for m in word['meanings']:
            l.append(f"<li>{m[0]} ({m[1]})</li>")
        meanings_txt = '\n'.join(l)

        l = []
        for m in word['word_parts']:
            l.append(f"{m[0]}={m[1]}")
        word_parts_txt = ', '.join(l)

        l = []
        for m in word['kanji_meanings_de']:
            l.append(f"{m[0]}={';'.join(m[1])}")
        kanji_meanings_de_txt = ', '.join(l)

        word_list.append(word)

    with open(f'../sentences/words-{num_learned_kanjis:04}.json', 'wt', encoding='utf-8') as file:
        json.dump(word_list, file, indent=4, ensure_ascii=False)

    print(f'{len(word_list)} words written')

    return common_words

def common_words_make_word_lists_lvls(max=50):
    for lvl in range(50, max+1, 50):
        common_words_make_word_lists(num_learned_kanjis=lvl)


def sentence_make_anki(lvl=50, reading_mode="Umschrift", high_values=[], low_values=[]):
    folder = f'../sentences/{lvl:04}'

    # sort
    list = sort_sentences(lvl, high_values=high_values, low_values=low_values)

    with open('card.css', 'rt') as file:
        css = file.read().strip()

    qfmt = '''
    <span class="sentence">{{Satz}}</span>
    '''

    afmt = '''
    <span class="sentence">{{Satz}}</span>
    <br/>
    <br/>
    <div style="text-align: start;">
        {{Tabelle}}<br/>
        {{Ton}}<br/>
        {{Bild}}<br/>
        <br/>
        {{Alt. Übersetzung}}<br/>
        {{Vokabeln}}
    </div>
    '''

    deck = genanki.Deck(
        1878758244 + lvl,
        f'Unterrichtsschriftzeichen - Sätze - Level {lvl}'
    )

    model = genanki.Model(
        1518892602,
        'Satz',
        fields=[
            {'name': 'Satz'},
            {'name': 'Übersetzung'},
            {'name': 'Tabelle'},
            {'name': 'Alt. Übersetzung'},
            {'name': 'Bild'},
            {'name': 'Ton'},
            {'name': 'Vokabeln'},
        ],
        templates=[
            {
                'name': 'Satz Karte',
                'qfmt': qfmt,
                'afmt': afmt
            }
        ],
        css=css,
        sort_field_index=0
    )

    media_files = []

    count = 0
    for entry in list:

        name, ext = os.path.splitext(entry['filename'])
        mp3_filename = name + '.mp3'
        mp3_file_path = os.path.join(folder, mp3_filename)

        jpg_filename = name + '.jpg'
        jpg_file_path = os.path.join(folder, jpg_filename)

        if not os.path.exists(mp3_file_path) or not os.path.exists(jpg_file_path):
            # print(f'missing media for {entry['filename']}')
            continue

        media_files.append(mp3_file_path)
        media_files.append(jpg_file_path)

        ul = '<ul>'
        for vocab in entry['generation']['used_vocabular']:
            found = next((sample for sample in entry['sample'] if sample['word'] == vocab['jp']), None)
            if not found:
                continue

            kanji_info = []
            for e in found['kanji_meanings_de']:
                kanji_info.append(f'{e[0]}={e[1][0]}')

            ul += '<li>'
            ul += f'{vocab['jp']} | {vocab['hiragana']} | {';'.join(kanji_info)}'
            ul += '<ul>'
            for meanings in found['meanings_de']:
                for meaning in meanings:
                    ul += f'<li>{meaning}</li>'
            ul += '</ul>'
            ul += '</li>'
        ul += '</ul>'

        guid = genanki.guid_for(entry['generation']['de'])

        note = genanki.Note(
            model=model,
            guid=guid,
            fields=[
                entry['generation']['jp'],
                entry['generation']['de'],
                entry['generation']['html_table'],
                entry['generation']['ja_de_deepl'],
                f'<img class="" src="{jpg_filename}">',
                # f'<audio controls><source src="{mp3_filename}" type="audio/mpeg"></audio>',
                f'[sound:{mp3_filename}]',
                ul
            ]
        )

        deck.add_note(note)

        count += 1

    package = genanki.Package([deck])
    package.media_files = media_files
    output_file = f'../anki/Unterrichtsschriftzeichen_Sätze-Level_{lvl:04}-{reading_mode}_Abfrage.apkg'
    package.write_to_file(output_file)

    print(f'{count} written')



def common_words_make_prompts(lvl=50, block_size=100, sample_count=10, sample_word_count=20, temperature=0.2):
    folder = f'../sentences/{lvl:04}'
    os.makedirs(folder, exist_ok=True)

    with open(f'../sentences/words-{lvl:04}.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

    with open("prompt_sentence_generation.txt", "r") as file:
        template = Template(file.read())

    common_words_blocks = chunk_list(common_words, block_size)

    for block_index, block in enumerate(common_words_blocks):

        #weights = np.array([1 / (i + 1) for i in range(len(block))])
        #weights /= weights.sum()

        for sample_index in range(sample_count):
            print(f'block {block_index+1}/{len(common_words_blocks)}, sample {sample_index+1}/{sample_count}')

            sample = np.random.choice(block, size=sample_word_count, replace=False) #, p=weights)

            str_list = ''
            for item in sample:
                str_list += f'* {item['word']} {item['hiragana']} {item['vocab_de']}\n'

            filled_prompt = template.substitute(str_list=str_list.strip())

            print('waiting for LLM...')
            try:
                completion = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": filled_prompt}],
                    temperature=temperature
                )
            except KeyboardInterrupt:
                print('keyboard interrupt')
                return

            answer_raw = completion.choices[0].message.content

            code_blocks = extract_code_blocks(answer_raw)

            if len(code_blocks) == 0:
                print('no code blocks found')
                continue

            code_block_str = code_blocks[0]

            entry = {}

            postfix = ''
            try:
                answer = json.loads(code_block_str)
                entry['generation'] = answer
            except Exception as e:
                entry['error'] = str(e)
                entry['answer_raw'] = answer_raw
                postfix = '_error'


            # meta data
            entry.update({
                'prompt': filled_prompt,
                'sample': list(sample),
                'config': {
                    'sample_word_count': sample_word_count,
                    'block_size': block_size,
                    'block_index': block_index,
                    'sample_index': sample_index,
                    'model': MODEL,
                    'temperature': temperature,
                    'datetime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            })

            with open(f'{folder}/{entry['config']['datetime']}{postfix}_{block_index}_{sample_index}.json', 'wt', encoding='utf-8') as file:
                json.dump(entry, file, indent=4, ensure_ascii=False)

            print('written')

def extract_code_blocks(text):
    matches = codeBlockPattern.findall(text)
    code_blocks = [match[2] for match in matches]
    return code_blocks

def chunk_list(lst, block_size):
    return [lst[i:i + block_size] for i in range(0, len(lst), block_size)]

def common_words_make_multimedia(lvl=50, multimedia=True, high_values=[], low_values=[]):
    folder = f'../sentences/{lvl:04}'
    os.makedirs(folder, exist_ok=True)

    # without api calls postprocess and save in file
    post_process_sentences_table_stats(lvl, folder)

    # sort
    list = sort_sentences(lvl, high_values=high_values, low_values=low_values)

    # filter
    list = [entry for entry in list if 'error' not in entry['filename']]

    # multimedia but based on sort above
    if multimedia:
        post_process_sentences_multimedia(list, folder)


def post_process_sentences_table_stats(lvl, folder):
    with open(f'../sentences/words-{lvl:04}.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

        common_words_dict = {}
        for common_word in common_words:
            common_words_dict[common_word['word']] = common_word

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

        all_kanjis = [entry['kanji'] for entry in kanji_kyouiku]

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith('json') or 'error' in filename:
            continue

        # filenames
        file_path = os.path.join(folder, filename)
        with open(file_path, 'rt', encoding='utf-8') as file:
            ctx = json.load(file)

        # print(file_path)

        jp_sent = ctx['generation']['jp']
        de_sent = ctx['generation']['de']

        # html table with vocabs
        if 'html_table' not in ctx['generation']:
            substrings = []
            for used_vocabular in ctx['generation']['used_vocabular']:
                common_word = common_words_dict.get(used_vocabular['jp'])
                # if not found in dictionary
                if common_word is None:
                    # fallback
                    common_word = {
                        'hiragana': used_vocabular['hiragana'],
                        'vocab_de': used_vocabular['de'],
                        'not_found': True
                    }
                substrings.append((used_vocabular['jp'], common_word))

            html_output = generate_highlighted_html(jp_sent, substrings, de_sent)

            ctx['generation']['html_table'] = html_output

        if 'stats' not in ctx:
            ctx['stats'] = stats(ctx, common_words_dict, all_kanjis, lvl)

        ctx['filename'] = filename

        with open(file_path, 'wt', encoding='utf-8') as file:
            json.dump(ctx, file, indent=4, ensure_ascii=False)


def post_process_sentences_multimedia(list, folder, api_wait_time=5):
    for entry in list:
        filename = entry['filename']

        # filenames
        name, ext = os.path.splitext(filename)

        mp3_filename = name + '.mp3'
        mp3_file_path = os.path.join(folder, mp3_filename)

        jpg_filename = name + '.jpg'
        jpg_file_path = os.path.join(folder, jpg_filename)

        file_path = os.path.join(folder, filename)
        with open(file_path, 'rt', encoding='utf-8') as file:
            ctx = json.load(file)

        print(file_path)

        jp_sent = ctx['generation']['jp']
        de_sent = ctx['generation']['de']

        api_call_used = False

        # text to speech
        if not os.path.exists(mp3_file_path):
            print(mp3_file_path)
            #time.sleep(api_wait_time)
            try:
                text_to_speech(jp_sent, mp3_file_path, 'ja')
            except:
                print('error')
            api_call_used = True

        # image generation
        if not os.path.exists(jpg_file_path):
            print(jpg_file_path)
            image_prompt = get_image_prompt(de_sent)
            ctx['generation']['image_prompt'] = image_prompt
            #time.sleep(api_wait_time)
            try:
                generate_image(jpg_file_path, image_prompt)
            except:
                print('error')
            api_call_used = True

        # translation check
        if 'ja_de_deepl' not in ctx['generation']:
            print('deepl ...')
            ctx['generation']['ja_de_deepl'] = translate_ja_de(jp_sent)
            # ctx['generation']['de_ja_deepl'] = translate_de_ja(ctx['generation']['ja_de_deepl'])

        with open(file_path, 'wt', encoding='utf-8') as file:
            json.dump(ctx, file, indent=4, ensure_ascii=False)

        print('done')
        if api_call_used:
            time.sleep(api_wait_time)


def sort_sentences(lvl=50, high_values=[], low_values=[]):
    folder = f'../sentences/{lvl:04}'
    list = []

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith('json') or 'error' in filename:
            continue

        file_path = os.path.join(folder, filename)
        with open(file_path, 'rt', encoding='utf-8') as file:
            ctx = json.load(file)

        list.append(ctx)

    keys = high_values + low_values

    # min max values
    min_max = {k: (min(obj['stats'][k] for obj in list), max(obj['stats'][k] for obj in list)) for k in keys}

    # normalized
    for obj in list:
        stats_norm = {}
        for k in keys:
            if min_max[k][1] > min_max[k][0]:
                norm_value = (obj['stats'][k] - min_max[k][0]) / (min_max[k][1] - min_max[k][0])
                stats_norm[k] = norm_value if k in high_values else (1 - norm_value if k in low_values else norm_value)
            else:
                stats_norm[k] = 0

        obj['score'] = sum(stats_norm.values())

    # sort
    list.sort(key=lambda x: x['score'], reverse=True)

    #for ctx in list:
    #    print(ctx['score'], ctx['generation']['jp'], ctx['generation']['de'])

    return list


def stats(ctx, common_words_dict, all_kanjis, lvl):
    jp_sent = ctx['generation']['jp']
    de_sent = ctx['generation']['de']

    lvl_kanjis = all_kanjis[:lvl]

    data = {
        'lvl': lvl,
        'jp_sent_len': len(jp_sent),
        'de_sent_len': len(de_sent),
        'de_sent_word_count': len(de_sent.split(' '))
    }

    #print(jp_sent)
    #print(de_sent)

    vocab_in_sent_match = 0
    vocab_in_sent_miss = 0

    vocab_in_dict_match = 0
    vocab_in_dict_miss = 0

    data['vocab_jp_lens'] = []
    data['vocab_hira_lens'] = []
    data['vocab_de_lens'] = []

    data['vocab_dict_lvls'] = []
    data['vocab_dict_indices'] = []

    for vocab in ctx['generation']['used_vocabular']:
        if vocab['jp'] in jp_sent:
            vocab_in_sent_match += 1
        else:
            vocab_in_sent_miss += 1

        if vocab['jp'] in common_words_dict:
            vocab_in_dict_match += 1
            entry = common_words_dict[vocab['jp']]
            index = list(common_words_dict.values()).index(entry)
            data['vocab_dict_indices'].append(index)
            data['vocab_dict_lvls'].append(entry['num_learned_kanjis'])
        else:
            vocab_in_dict_miss += 1

        data['vocab_jp_lens'].append(len(vocab['jp']))
        data['vocab_hira_lens'].append(len(vocab['hiragana']))
        data['vocab_de_lens'].append(len(vocab['de']))

    data['vocab_jp_lens_mean'] = statistics.mean(data['vocab_jp_lens'])
    data['vocab_hira_lens_mean'] = statistics.mean(data['vocab_hira_lens'])
    data['vocab_de_lens_mean'] = statistics.mean(data['vocab_de_lens'])
    data['vocab_dict_lvls_mean'] = statistics.mean(data['vocab_dict_lvls'])
    data['vocab_dict_indices_mean'] = statistics.mean(data['vocab_dict_indices'])

    data['vocab_in_sent_match'] = vocab_in_sent_match
    data['vocab_in_sent_miss'] = vocab_in_sent_miss
    data['vocab_in_dict_match'] = vocab_in_dict_match
    data['vocab_in_dict_miss'] = vocab_in_dict_miss
    data['vocab_len'] = len(ctx['generation']['used_vocabular'])

    jp_sent_copy : str = jp_sent
    for vocab in ctx['generation']['used_vocabular']:
        jp_sent_copy = jp_sent_copy.replace(vocab['jp'], '')

    data['jp_sent_miss_len'] = len(jp_sent_copy)
    data['jp_sent_miss_ratio'] = data['jp_sent_miss_len'] / data['jp_sent_len']
    data['jp_sent_miss'] = jp_sent_copy

    data['jp_sent_miss_hiragana'] = 0
    data['jp_sent_miss_katakana'] = 0
    data['jp_sent_miss_lvl_kanji'] = 0
    data['jp_sent_miss_kyouiku_kanji'] = 0
    data['jp_sent_miss_joyo_kanji'] = 0
    data['jp_sent_miss_remaining'] = []
    for c in data['jp_sent_miss']:
        if is_hiragana(c):
            data['jp_sent_miss_hiragana'] += 1
        elif is_katakana(c):
            data['jp_sent_miss_katakana'] += 1
        elif c in lvl_kanjis:
            data['jp_sent_miss_lvl_kanji'] += 1
        elif c in KYOUIKU_STR:
            data['jp_sent_miss_kyouiku_kanji'] += 1
        elif c in JOYO_STR:
            data['jp_sent_miss_joyo_kanji'] += 1
        else:
            data['jp_sent_miss_remaining'].append(c)


    return data


def generate_highlighted_html(sentence, substrings, de_sent):
    substrings = sorted(substrings, key=len, reverse=True)

    found_substrings = []
    for substring in substrings:
        pos = sentence.find(substring[0])
        if pos != -1:
            found_substrings.append((pos, pos + len(substring[0]), substring))

    found_substrings.sort()

    first_row = []
    second_row = []
    last_pos = 0

    for start, end, substring in found_substrings:
        # miss
        if start > last_pos:
            first_row.append(f"  <td>{sentence[last_pos:start]}</td>\n")
            second_row.append(f"  <td></td>\n")

        # match
        first_row.append(f"  <td>{sentence[start:end]}</td>\n")
        not_found_style = ' style="color: gray;"' if 'not_found' in substring[1] else ''
        second_row.append(f"  <td{not_found_style}>{substring[1]['hiragana']}<br/>{substring[1]['vocab_de']}<br/></td>\n")

        last_pos = end

    # Add remaining miss
    if last_pos < len(sentence):
        first_row.append(f"  <td>{sentence[last_pos:]}</td>\n")
        second_row.append(f"  <td></td>\n")

    html_table = f"<table>\n<tr>\n{''.join(first_row)}</tr>\n<tr>\n{''.join(second_row)}</tr>\n<tr>\n  <td colspan=\"{len(first_row)}\">{de_sent}</td>\n</tr>\n</table>"

    return html_table


def get_image_prompt(de_sent, temperature=0.7):
    with open("prompt_image_prompt.txt", "r") as file:
        template = Template(file.read())

    filled_prompt = template.substitute(de_sent=de_sent)

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": filled_prompt}],
        temperature=temperature
    )

    answer_raw = completion.choices[0].message.content
    return answer_raw