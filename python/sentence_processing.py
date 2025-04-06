import csv
import gzip
import json
import os
import random
import re
import time
from datetime import datetime

import genanki
from tqdm import tqdm

import hiragana
from common_word_processing import get_image_prompt
from deepl_api import translate_ja_de
from img_gen import generate_image
from tts import text_to_speech


# first we run through sentences and decompose them based on the vocabulary we would like to learn
# a lot of meta data is in the json if details is set, but we should add it later
def collect_sentences(lvl=1050, details=False, output_file_path="../sentences/sentences.jsonl.gz"):
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

        kanji_kyouiku_dict = {}
        for l, entry in enumerate(kanji_kyouiku):
            entry['lvl'] = l
            kanji_kyouiku_dict[entry['kanji']] = entry


    with open(f'../sentences/words-{lvl:04}.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

        common_words_dict = {}
        for i, common_word in enumerate(common_words):
            if common_word['word'] in common_words_dict:
                raise Exception(f'{common_word['word']} duplicate: {common_words_dict[common_word['word']]}')

            common_word['position'] = i
            common_words_dict[common_word['word']] = common_word


    sorted_strings = sorted(list(common_words_dict.keys()), key=len, reverse=True)
    pattern_str = "|".join(map(re.escape, sorted_strings))
    pattern = re.compile(pattern_str, re.IGNORECASE)

    with gzip.open(output_file_path, "wt", encoding="utf-8") as jsonl:

        # ja en 275.928
        # ja de  57.635
        tatoeba('../sentences-resource/Sentence pairs in Japanese-English - 2025-02-19.tsv', pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl)
        tatoeba('../sentences-resource/Sentence pairs in Japanese-German - 2025-02-19.tsv', pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl, tl_key='de')

        # 25.740.835
        # jparacrawl(pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl)


def jparacrawl(pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl):
    with open('../sentences-resource/en-ja/en-ja.bicleaner05.txt', 'r', newline='',
              encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')

        for i, row in enumerate(tqdm(reader)):
            obj = {
                'id': f'jparacrawl-{i}',
                'source': 'jparacrawl',
                'ja': row[4],
                'en': row[3],
                'ja_len': len(row[4]),
                'en_len': len(row[3]),
                'value': float(row[2])
            }

            process_obj(obj, pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl)


def tatoeba(file_path, pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl, tl_key='en'):
    # from https://tatoeba.org/en/downloads
    with open(file_path, 'r', newline='',
              encoding='utf-8-sig') as file:
        reader = csv.reader(file, delimiter='\t')  # Specify tab as the delimiter

        for row in tqdm(reader):
            obj = {
                'id': f'tatoeba-{row[0]}-{row[2]}',
                'source': 'tatoeba',
                'ja': row[1],
                tl_key: row[3],
                'ja_len': len(row[1]),
                tl_key + '_len': len(row[3])
            }

            process_obj(obj, pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl)


def process_obj(obj, pattern, common_words_dict, kanji_kyouiku_dict, details, jsonl):
    result = longest_match_regex(pattern, obj['ja'])

    used_words = []
    used_kanjis_kyouiku = set()
    used_kanjis_joyo = set()
    used_kanjis_unknown = set()

    positions = []
    lvls = []
    match_lens = []
    miss_lens = []

    for entry in result:
        if entry['match']:
            vocab = common_words_dict[entry['text']]

            # makes it larger but more complete
            if details:
                entry['vocab'] = vocab

            used_words.append(vocab['word'])

            positions.append(vocab['position'])
            lvls.append(vocab['num_learned_kanjis'])

            match_lens.append(len(entry['text']))

        else:
            miss_lens.append(len(entry['text']))

        # for both check the kanji usage
        for c in entry['text']:
            if c in hiragana.KYOUIKU_STR:
                used_kanjis_kyouiku.add(c)
            elif c in hiragana.JOYO_STR:
                used_kanjis_joyo.add(c)
            elif hiragana.is_kanji(c):
                used_kanjis_unknown.add(c)

    obj['parts'] = result

    # the kanji view
    obj['kanjis_kyouiku'] = list(used_kanjis_kyouiku)
    obj['kanjis_joyo'] = list(used_kanjis_joyo)
    obj['kanjis_unknown'] = list(used_kanjis_unknown)
    obj['kanjis_kyouiku_details'] = []
    obj['kanjis_kyouiku_lvls'] = []
    for k in used_kanjis_kyouiku:
        # if k not in kanji_kyouiku_dict:
        #    print(row)
        #    print(used_kanjis_kyouiku)
        entry = kanji_kyouiku_dict[k]
        obj['kanjis_kyouiku_lvls'].append(entry['lvl'])
        # this makes it more complete
        if details:
            obj['kanjis_kyouiku_details'].append(entry)

    obj['kanjis_kyouiku_lvls_max'] = max(obj['kanjis_kyouiku_lvls'], default=0)

    # the words view
    obj['words'] = used_words
    # word positions (lower position = higher frequency)
    obj['words_positions'] = positions
    obj['words_positions_avg'] = avg(positions, default=-1)
    # kanji used in words their level
    obj['words_lvls'] = lvls
    obj['words_lvls_max'] = max(lvls, default=0)

    obj['miss_lens'] = miss_lens
    obj['miss_count'] = len(miss_lens)
    obj['miss_sum'] = sum(miss_lens)

    obj['match_lens'] = match_lens
    obj['match_count'] = len(match_lens)
    obj['match_sum'] = sum(match_lens)

    # add summary to fast find good sentences
    # * max number learned kanji for all kanji which are used
    # * all vocab positions to get sentences with rather lower positions means high frequent
    # * used vocab and used kanji to sort the sentences by vocab usage to avoid using the same vocab/kanji again
    # * remaining non-match parts len and count

    match_ratio = obj['match_sum'] / (obj['match_sum'] + obj['miss_sum'])
    obj['match_ratio'] = match_ratio

    # * for easy filtering put some numbers in front of json

    jsonl.write(str(obj['kanjis_kyouiku_lvls_max']))
    jsonl.write(' ')
    jsonl.write(str(len(obj['kanjis_joyo'])))
    jsonl.write(' ')
    jsonl.write(str(len(obj['kanjis_unknown'])))
    jsonl.write(' ')
    json.dump(obj, jsonl, ensure_ascii=False)
    jsonl.write("\n")


def longest_match_regex(pattern, text):
    last_end = 0
    result = []

    for match in re.finditer(pattern, text):
        start, end = match.span()

        if start > last_end:
            result.append({
                'text': text[last_end:start],
                'match': False
            })

        result.append({
            'text': match.group(),
            'match': True
        })
        last_end = end

    if last_end < len(text):
        result.append({
            'text': text[last_end:],
            'match': False
        })

    return result


def avg(numbers, default=0):
    return sum(numbers) / len(numbers) if numbers else default


def write_sentences(lvl=50, common_words_max=500, word_threshold_start=5, sentence_freshness_start=5, input_file_path=None, output_file_path=None):
    # read and coarse grain filter
    with gzip.open("../sentences/sentences.jsonl.gz", "rt", encoding="utf-8") as jsonl:
        subset = []

        for line in jsonl:
            segments = line.split(maxsplit=3)

            kanjis_kyouiku_lvls_max = int(segments[0])
            kanjis_joyo_len = int(segments[1])
            kanjis_unknown_len = int(segments[2])

            if kanjis_kyouiku_lvls_max > 0 and kanjis_kyouiku_lvls_max <= lvl and kanjis_joyo_len == 0 and kanjis_unknown_len == 0:
                line = line[line.find("{"):]
                line_obj = json.loads(line)
                subset.append(line_obj)

    if input_file_path:
        with open(input_file_path, 'rt', encoding='utf-8') as file:
            input = json.load(file)
            will_be_learned = set(input['will_be_learned'])
            to_be_learned = set(input['to_be_learned'])
            learned_sentences = input['learned_sentences']
            sentence_cache = set(sent['ja'] for sent in learned_sentences)
    else:
        to_be_learned = set()
        will_be_learned = set()
        learned_sentences = []
        sentence_cache = set()

    # words of that level
    all_words = set()
    with open(f'../sentences/words-{lvl:04}.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)

        for entry in common_words[:common_words_max]:
            to_be_learned.add(entry['word'])
            all_words.add(entry['word'])


    will_be_learned_init = len(will_be_learned)
    to_be_learned_init = len(to_be_learned)
    learned_sentences_init = len(learned_sentences)
    print('lvl', lvl)
    print('inital will_be_learned', will_be_learned_init)
    print('inital to_be_learned', to_be_learned_init)
    print('inital learned_sentences', learned_sentences_init)
    # print('inital sentence_cache', len(sentence_cache))

    sentence_freshness = sentence_freshness_start
    word_threshold = word_threshold_start
    index = 0

    while True:
        selection = []

        # fine grain filter: word rich sentences first
        for entry in subset:
            if len(entry['words']) > word_threshold:
                selection.append(entry)

        # low miss_sum and high len(words) and low words_positions_avg
        sort_sentences(selection, low_values=['miss_sum', 'ja_len', 'words_positions_avg'])

        for entry in selection:
            words = set(entry['words'])

            # words of interest in vocab list
            words_of_interest = all_words.intersection(words)

            # minimize
            already_learned = will_be_learned.intersection(words_of_interest)

            # maximize
            not_yet_learned = to_be_learned.intersection(words_of_interest)

            pick = len(not_yet_learned) > len(already_learned) + sentence_freshness and entry['ja'] not in sentence_cache

            if pick:
                for word in words_of_interest:
                    will_be_learned.add(word)
                    to_be_learned.discard(word)
                learned_sentences.append(entry)
                sentence_cache.add(entry['ja'])


        # reduce the options
        if index == 0:
            sentence_freshness = max(sentence_freshness - 1, 0)
        elif index == 1:
            word_threshold = max(word_threshold - 1, 0)

        index += 1
        index %= 2

        if sentence_freshness == 0 and word_threshold == 0:
            break

    #for i, sent in enumerate(learned_sentences):
    #    print(i, sent['ja'], sent['words'])

    gain = len(will_be_learned) / len(learned_sentences)
    coverage = len(will_be_learned) / len(all_words)

    # sentences with frequent words first
    learned_sentences.sort(key=lambda x: x['words_positions_avg'])

    if output_file_path:
        data = {
            'lvl': lvl,
            'common_words_max': common_words_max,
            'word_threshold_start': word_threshold_start,
            'sentence_freshness_start': sentence_freshness_start,
            'datetime': datetime.now().isoformat(),
            'will_be_learned_len': len(will_be_learned),
            'to_be_learned_len': len(to_be_learned),
            'learned_sentences_len': len(learned_sentences),
            'will_be_learned': list(will_be_learned),
            'to_be_learned': list(to_be_learned),
            'learned_sentences': learned_sentences
        }

        with open(output_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


    print(f'{len(subset)} subset')
    print(f'{len(selection)} selection')
    print(f'{len(all_words)} all_words')
    print(f'{len(common_words)} in level {lvl}')

    print(f'{word_threshold_start} word_threshold_start')
    print(f'{sentence_freshness_start} sentence_freshness_start')

    print(f'{len(learned_sentences)} learned_sentences, diff: {len(learned_sentences) - learned_sentences_init}')
    print(f'{len(will_be_learned)} will_be_learned, diff: {len(will_be_learned) - will_be_learned_init}')
    print(f'{len(to_be_learned)} to_be_learned, diff: {len(to_be_learned) - to_be_learned_init}')

    print(f'{gain:.03} gain')
    print(f'{coverage:.03} coverage')


def sort_sentences(sentences, high_values=[], low_values=[], reverse=False):
    if len(sentences) == 0:
        return sentences

    keys = high_values + low_values

    # min max values
    min_max = {k: (min(obj[k] for obj in sentences), max(obj[k] for obj in sentences)) for k in keys}

    # normalized
    for obj in sentences:
        stats_norm = {}
        for k in keys:
            if min_max[k][1] > min_max[k][0]:
                norm_value = (obj[k] - min_max[k][0]) / (min_max[k][1] - min_max[k][0])
                stats_norm[k] = norm_value if k in high_values else (1 - norm_value if k in low_values else norm_value)
            else:
                stats_norm[k] = 0

        obj['score'] = sum(stats_norm.values())

    sentences.sort(key=lambda x: x['score'], reverse=(not reverse))

    return sentences

# use this after write_sentences
def multimedia_sentences(input_file_path, cache_folder, include_tts=True, include_img=True, include_transl=True, api_wait_time=5, transl_text_len=4):
    os.makedirs(cache_folder, exist_ok=True)

    # sentences ctx file
    with open(input_file_path, 'rt', encoding='utf-8') as file:
        sentences_ctx = json.load(file)

    print(len(sentences_ctx['learned_sentences']), 'sentences')

    for sent in sentences_ctx['learned_sentences']:
        ja = sent['ja']
        transl = sent['en'] if 'en' in sent else sent['de']

        id = sent['id']
        mp3_file_path = os.path.join(cache_folder, f'{id}.mp3')
        jpg_file_path = os.path.join(cache_folder, f'{id}.jpg')

        print(id)

        api_call_used = False

        if include_tts and not os.path.exists(mp3_file_path):
            print(mp3_file_path)
            try:
                text_to_speech(ja, mp3_file_path, 'ja')
            except:
                print('error')
            api_call_used = True

        if include_img and not os.path.exists(jpg_file_path):
            print(jpg_file_path)
            image_prompt = get_image_prompt(transl)
            sent['image_prompt'] = image_prompt
            try:
                generate_image(jpg_file_path, image_prompt)
            except:
                print('error')
            api_call_used = True

        # translation check
        if include_transl and 'ja_de_deepl' not in sent:
            print('ja_de_deepl sent')
            sent['ja_de_deepl'] = translate_ja_de(ja)

        for part in sent['parts']:
            if not part['match'] and len(part['text']) >= transl_text_len and 'ja_de_deepl' not in part:
                print('ja_de_deepl part')
                part['ja_de_deepl'] = translate_ja_de(part['text'])

        with open(input_file_path, 'wt', encoding='utf-8') as file:
            json.dump(sentences_ctx, file, indent=2, ensure_ascii=False)

        if api_call_used:
            print('done, wait...')
            time.sleep(api_wait_time)


def make_anki_sentences(input_file_path, cache_folder):

    # sentences ctx file
    with open(input_file_path, 'rt', encoding='utf-8') as file:
        sentences_ctx = json.load(file)
        lvl = sentences_ctx['lvl']

    # aux data
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)
        kanji_kyouiku_dict = {}
        for l, entry in enumerate(kanji_kyouiku):
            entry['lvl'] = l
            kanji_kyouiku_dict[entry['kanji']] = entry

    # aux data
    with open(f'../sentences/words-{lvl:04}.json', 'rt', encoding='utf-8') as file:
        common_words = json.load(file)
        common_words_dict = {}
        for i, common_word in enumerate(common_words):
            if common_word['word'] in common_words_dict:
                raise Exception(f'{common_word['word']} duplicate: {common_words_dict[common_word['word']]}')
            common_word['position'] = i
            common_words_dict[common_word['word']] = common_word

    # aux data
    with open('card.css', 'rt') as file:
        css = file.read().strip()

    # anki settings
    qfmt = '''
        <span class="sentence">{{Satz}}</span>
        '''

    afmt = '''
        <span class="sentence">{{Satz}}</span>
        <br/>
        <br/>
        <div style="text-align: start;">
            {{Tabelle}}<br/>
            {{Übersetzung}}<br/>
            {{Alt. Übersetzung}}<br/>
            {{Ton}}<br/>
            {{Bild}}<br/>
            <br/>
            {{Vokabeln}}<br/>
            {{Kanjis}}
        </div>
        '''

    deck = genanki.Deck(
        2050612111,
        f'Unterrichtsschriftzeichen - Sätze'
    )

    model = genanki.Model(
        1613000730,
        'Satz',
        fields=[
            {'name': 'Satz Position'},
            {'name': 'Satz'},
            {'name': 'Übersetzung'},
            {'name': 'Tabelle'},
            {'name': 'Alt. Übersetzung'},
            {'name': 'Bild'},
            {'name': 'Ton'},
            {'name': 'Vokabeln'},
            {'name': 'Kanjis'},
        ],
        templates=[
            {
                'name': 'Satz Karte',
                'qfmt': qfmt,
                'afmt': afmt
            }
        ],
        css=css,
        sort_field_index=0 # = int(words_positions_avg)
    )

    media_files = []

    # sentences ctx file
    with open(input_file_path, 'rt', encoding='utf-8') as file:
        sentences_ctx = json.load(file)

    print(len(sentences_ctx['learned_sentences']), 'sentences')

    count = 0
    for sent in sentences_ctx['learned_sentences']:

        warn_not_found = False
        # update missing vocab data
        for part in sent['parts']:
            if part['match']:
                part['vocab'] = common_words_dict.get(part['text'])
                if part['vocab'] == None:
                    print('[WARN]', part['text'], 'not found')
                    warn_not_found = True
                    break

        if warn_not_found:
            continue

        # update missing kanji data
        sent['kanji_details'] = []
        # sort by occurances
        sent['kanjis_kyouiku'].sort(key=lambda x: sent['ja'].index(x))
        for kanji in sent['kanjis_kyouiku']:
            sent['kanji_details'].append(kanji_kyouiku_dict[kanji])

        transl = sent['de'] if 'de' in sent else sent['ja_de_deepl']

        id = sent['id']
        mp3_filename = f'{id}.mp3'
        jpg_filename = f'{id}.jpg'
        mp3_file_path = os.path.join(cache_folder, mp3_filename)
        jpg_file_path = os.path.join(cache_folder, jpg_filename)

        if not os.path.exists(mp3_file_path) or not os.path.exists(jpg_file_path):
            continue

        media_files.append(mp3_file_path)
        media_files.append(jpg_file_path)

        print(id)

        guid = genanki.guid_for(id)

        note = genanki.Note(
            model=model,
            guid=guid,
            fields=[
                str(int(sent['words_positions_avg'])),
                get_vocab_text(sent['parts']), # sent['ja'],
                transl,
                get_html_table(sent['parts']),
                sent['en'] if 'en' in sent else '',
                f'<img class="" src="{jpg_filename}">',
                # f'<audio controls><source src="{mp3_filename}" type="audio/mpeg"></audio>',
                f'[sound:{mp3_filename}]',
                get_vocab_ul(sent['parts']),
                get_kanji_ul(sent['kanji_details'])
            ]
        )

        deck.add_note(note)

        count += 1

    package = genanki.Package([deck])
    package.media_files = media_files
    output_file = f'../anki/Unterrichtsschriftzeichen_Sätze-Level_{lvl:04}.apkg'
    package.write_to_file(output_file)

    print(f'{count} written')


def get_html_table(parts):
    html_table = ""
    html_table += "<table>"

    html_table += "<tr>"
    for part in parts:
        html_table += f"<td class=\"{ 'td_match' if part['match'] else 'td_miss' }\">"

        html_table += f"{part['text']}"
        html_table += "<br/>"

        if part['match']:
            vocab = part['vocab']

            # all hiragana possibilities
            hira = [vocab['hiragana']]
            for i in range(0, 10):
                key = f'word_parts_{i}'
                if key in vocab:
                    h = ""
                    for wp in vocab[key]:
                        h += wp[1]  # hiragana
                    hira.append(h)

            html_table += ', '.join(hira)

        html_table += "<br/>"

        if part['match']:
            html_table += f"{part['vocab']['vocab_de']}"
        elif 'ja_de_deepl' in part:
            html_table += f"{part['ja_de_deepl']}"

        html_table += "</td>"
    html_table += "</tr>"

    # html_table += f"<tr><td colspan=\"{len(parts)}\">{transl}</td></tr>"

    html_table += "</table>"
    return html_table

def get_vocab_text(parts):
    text = ''
    for part in parts:
        cl = ''
        if 'vocab' not in part:
            cl = 'text_miss'
        else:
            cl = 'text_match'

        text += f'<span class="{cl}">'
        text += part['text']
        text += '</span>'

    return text

def get_vocab_ul(parts):
    ul = '<ul>'
    for part in parts:
        if 'vocab' not in part:
            continue

        vocab = part['vocab']

        kanji_info = []
        for e in vocab['kanji_meanings_de']:
            kanji_info.append(f'{e[0]}={e[1][0]}')

        hira = [vocab['hiragana']]
        for i in range(0,10):
            key = f'word_parts_{i}'
            if key in vocab:
                h = ""
                for wp in vocab[key]:
                    h += wp[1] # hiragana
                hira.append(h)

        ul += '<li>'
        ul += f'{vocab['word']} | {', '.join(hira)} | {' '.join(kanji_info)}'
        ul += '<ul>'
        for meanings in vocab['meanings_de']:
            for meaning in meanings:
                ul += f'<li>{meaning}</li>'
        ul += '</ul>'
        ul += '</li>'
    ul += '</ul>'

    return ul


def get_kanji_ul(kanji_details):
    ul = '<ul>'
    for entry in kanji_details:
        ul += '<li>'
        ul += f'{entry['kanji']}'

        meanings_str = ', '.join(m for m in entry['meanings_de'])

        ul += '<ul>'
        ul += f'<li>{meanings_str}</li>'
        ul += f'<li>{entry['mnemonic_reading_de']}</li>'
        ul += f'<li>{entry['mnemonic_meaning_de']}</li>'
        ul += '</ul>'

        ul += '</li>'
    ul += '</ul>'

    return ul