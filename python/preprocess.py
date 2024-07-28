from hiragana import hiragana_to_romaji, hiragana_to_ascii
import csv
import gzip
from collections import defaultdict
import json
import os
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup


def hiragana_check_dict():
    with gzip.open('../dict-pos_comma.csv.gz', mode='rt', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    print(len(rows), 'rows')

    ctxs = []

    for hiragana, ascii in hiragana_to_ascii.items():
        # print(hiragana, ascii)

        ctx = {}
        ctx['hiragana'] = hiragana
        ctx['ascii'] = ascii
        ctx['match_rows'] = []
        ctx['match_rows_contains'] = []
        ctx['langs'] = defaultdict(int)
        ctx['pos'] = defaultdict(int)

        for row in rows:
            test_asciis = [ascii]
            if 'y' in ascii:
                test_asciis.append(ascii.replace('y', 'i'))
                test_asciis.append(ascii.replace('y', 'ie'))
                test_asciis.append(ascii.replace('y', 'ih'))

            for test_ascii in test_asciis:
                if row[0].lower().startswith(test_ascii):
                    ctx['match_rows'].append(row)
                    ctx['langs'][row[1]] += 1
                    ctx['pos'][row[2]] += 1

            for test_ascii in test_asciis:
                if test_ascii in row[0].lower():
                    ctx['match_rows_contains'].append(row)

        ctxs.append(ctx)

        #print()
        #print()
        #print(ctx['hiragana'], ctx['ascii'], len(ctx['match_rows']), ctx['langs'], ctx['pos'])

    ctxs = sorted(ctxs, key=lambda x: len(x['match_rows']), reverse=True)

    for ctx in ctxs:
        print(ctx['hiragana'], ctx['ascii'], len(ctx['match_rows']), ctx['langs'], ctx['pos'])

        if len(ctx['match_rows']) < 150:
            for row in ctx['match_rows']:
                print('\t', row)
            for row in ctx['match_rows_contains']:
                print('\t', row, 'contains')


def kanji_check():
    os.makedirs("export", exist_ok=True)


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

                # romaji = hiragana_to_romaji(yomi)
                #if romaji is None:
                #    print('test')

                yomi_dict[yomi] += 1

                for meaning in data['wk_meanings']:
                    if meaning.startswith('!') or meaning.startswith('^'):
                        continue

                    yomi2meaning[yomi].append(meaning)
                # print('\t', yomi, romaji)

    #print(yomi_dict)

    with gzip.open('../dict-pos_comma.csv.gz', mode='rt', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = [row for row in reader]

    print(len(rows), 'rows')

    # we have 334 words because some are used for multiple meanings
    print(len(yomi_dict.keys()), ' yomi words')

    langs = ['de', 'en']
    ctxs = []

    # ok now we have all the word how they are read most commonly
    for k,v in tqdm(dict(sorted(yomi_dict.items(), key=lambda item: item[1], reverse=True)).items()):
        romaji = hiragana_to_romaji(k)

        ctx = {}
        ctx['hiragana'] = k
        ctx['romaji'] = romaji
        ctx['frequency'] = v

        ctxs.append(ctx)

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
            ("tsu", "TTsu")
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

                        # shortest first
                        ctx[f'match_rows_{mode}_{row[2]}'].sort(key=lambda x: len(x[0]))

        ctx['meanings'] = yomi2meaning[ctx['hiragana']]

        count = len(ctx['match_rows_start_de'])
        if count == 0:
            count = len(ctx['match_rows_end_de'])

        # _{len(ctx['match_rows_end_de'])}_{len(ctx['match_rows_contains_de'])}
        with open(f'export/{ctx['romaji']}_{count}__{ctx['frequency']}.json', 'wt') as file:
            json.dump(ctx, file, indent=2)

        #print()
        #print(ctx['hiragana'], yomi2meaning[ctx['hiragana']], len(yomi2meaning[ctx['hiragana']]), ctx['romaji'], ctx['frequency'], len(ctx['match_rows_start_de']), len(ctx['match_rows_start_de']), len(ctx['match_rows_contains_de']))

        #for match in ctx['match_rows_start_de'][:10]:
        #    print(match, 'start')
        #for match in ctx['match_rows_end_de'][:10]:
        #    print(match, 'end')
        #for match in ctx['match_rows_contains_de'][:10]:
        #    print(match, 'contains')


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


# add_german()
# radicals_check()
# dict_to_array()
prepare_mnemonics()