import glob
import json
import os

import genanki

import hiragana
from helper import is_done, get_reading_strs

def mnemonic_reading_de_fix():
    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    for entry in kanji_kyouiku:
        if entry['mnemonic_reading_de_done']:
            continue

        yomi_list = []
        for yomi in entry['readings_on'] + entry['readings_kun']:
            is_on = yomi in entry['readings_on']
            yomi = yomi.replace('!', '').replace('^', '')
            mode = 'onyomi' if is_on else 'kunyomi'
            romaji = hiragana.hiragana_to_romaji(yomi)

        if 'reading_dist' not in entry:
            # print('[WARN]', entry['kanji'], 'no reading dist')
            # fix
            entry['reading_dist'] = []

        for reading in entry['reading_dist']:

            if reading['prop'] < 0.05:
                continue

            selected_mode = 'unknown'
            for yomi in entry['readings_on'] + entry['readings_kun']:
                is_on = yomi in entry['readings_on']
                mode = 'onyomi' if is_on else 'kunyomi'
                yomi : str = yomi.replace('-', '').replace('.', '')

                if yomi.startswith(reading['reading']):
                    selected_mode = mode
                    break

            if selected_mode == 'unknown':
                continue

            romaji = hiragana.hiragana_to_romaji(reading['reading'])
            yomi_list.append(f"<span class='reading {selected_mode}' data-hiragana='{reading['reading']}'>{romaji}</span> <span class='hiragana'>({reading['reading']})</span>")

        yomi_part = '  '.join(yomi_list)

        meaning_part = f"<span class='meaning' data-kanji='{entry['kanji']}'>{entry['meanings_de'][0]}</span> <span class='meaning_kanji_reading'>({entry['kanji']})</span>"

        mnemonic_reading_de = f"{meaning_part} , {yomi_part}"

        entry['mnemonic_reading_de'] = mnemonic_reading_de

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'wt', encoding='utf-8') as file:
        json.dump(kanji_kyouiku, file, indent=4, ensure_ascii=False)

def make_anki_v2(romaji_reading=False, separator=" "):
    os.makedirs('../anki', exist_ok=True)

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
        'Merksatz', # 'Kyōiku-Kanji Deutsch Bedeutung/Lesung Merksatz',
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
        'Merkbild', # 'Kyōiku-Kanji Deutsch Bedeutung/Lesung Merkbild',
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
        'Unterrichtsschriftzeichen', #'Kyōiku-Kanji Deutsch'
    )
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

    reading_mode = "Umschrift" if romaji_reading else "Hiragana"
    output_file = f'../anki/Unterrichtsschriftzeichen_{reading_mode}_Abfrage.apkg'
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

