import csv
import gzip
import json
import os
import pickle
import sys
from collections import defaultdict

import genanki
from tqdm import tqdm

from frequency import frequency_crawler
from helper import get_reading_strs, remove_brackets
from hiragana import hiragana_to_romaji
from jisho_processing import jisho_collect_common_words
from wadoku_processing import wadoku_load


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

    with open('../kanji-kyouiku-verbs-wip.json', 'rt', encoding='utf-8') as file:
        kyouiku_verbs = json.load(file)

        kyouiku_verbs_dict = {}
        for entry in kyouiku_verbs:
            kyouiku_verbs_dict[entry['word']] = entry

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
    {{FrontSide}}<br/>
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

        if word['word'] in kyouiku_verbs_dict:
            filtered_verbs.append(word)
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
    output_file = f'../anki/Unterrichtsschriftzeichen_Gebraeuchliche_Woerter-Level_{num_learned_kanjis}-{reading_mode}_Abfrage.apkg'
    package.write_to_file(output_file)

    print(count, 'written,', 'num_learned_kanjis:', num_learned_kanjis, 'filtered_verbs:', len(filtered_verbs), 'wadoku_not_found_count:', wadoku_not_found_count)


def common_words_make_anki_lvls():
    #max = 1050
    max = 250
    #max = 51
    for lvl in range(50, max, 50):
        common_words_make_anki(num_learned_kanjis=lvl)


