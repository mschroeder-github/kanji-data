import csv
import gzip
import json
from collections import defaultdict

from tqdm import tqdm

from hiragana import hiragana_to_romaji


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



# def make_anki(romaji_reading=False, separator=" ", meaning_kanji_bg="#fffee6", reading_kanji_bg="#e6fffd"):
#     with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
#         kanji_kyouiku = json.load(file)
#
#     qfmt_meaning = '''
# <b>Bedeutung</b> von
# <br/>
# <br/>
# <span class="kanji">{{Kanji}}</span>
# <br/>
# <br/>
# {{type:Bedeutung}}
#     '''
#
#     reading_mode = "Romaji" if romaji_reading else "Hiragana"
#
#     qfmt_reading = '''
# <b>Lesung</b> von
# <br/>
# <br/>
# <span class="kanji">{{Kanji}}</span>
# <br/>
# <br/>
# ''' + '{{type:Lesung' + reading_mode + '}}'
#
#     afmt_prefix = '''
#     {{FrontSide}}
#     '''
#
#     afmt_postfix = '''
#     <br/>
#     <span class="additional additional_de">{{Bedeutung_Weitere_Deutsch}}</span><br/>
#     <span class="additional additional_en">{{Bedeutung_Weitere_Englisch}}</span>
#     '''
#
#     # three models
#     # * meaning -> mnemonic
#     # * meaning -> image
#     # * reading -> mnemonic
#
#     mnemonic_meaning = genanki.Model(
#         1869128057,
#         'Kyōiku-Kanji Deutsch Bedeutung Merksatz',
#         fields=[
#             {'name': 'Kanji'},
#             {'name': 'Bedeutung'},
#             {'name': 'Bedeutung_Weitere_Deutsch'},
#             {'name': 'Bedeutung_Weitere_Englisch'},
#             {'name': 'Merksatz'}
#         ],
#         templates=[
#             {
#                 'name': 'Bedeutung Merksatz Karte',
#                 'qfmt': qfmt_meaning,
#                 'afmt': afmt_prefix + '<br/><br/>{{Merksatz}}<br/>' + afmt_postfix,
#             }
#         ],
#         css="""
#         .card {
#             text-align: center;
#         }
#         .meaning {
#             font-weight: bold;
#             border: 0px solid black;
#             border-radius: 5px;
#             padding: 3px;
#         }
#         .radical {
#             font-weight: bold;
#             border: 0px solid black;
#             border-radius: 5px;
#             padding: 3px;
#             background-color: #a3ffb3;
#         }
#         .kanji {
#             font-size: 50px;
#             padding: 10px;""" +
#             f"background-color: {meaning_kanji_bg};" +
#             """
#             }
#             .additional {
#                 font-size: small;
#             }
#             .additional_en {
#                 color: gray;
#             }
#             """
#     )
#
#     image_meaning = genanki.Model(
#         1801052884,
#         'Kyōiku-Kanji Deutsch Bedeutung Merkbild',
#         fields=[
#             {'name': 'Kanji'},
#             {'name': 'Bedeutung'},
#             {'name': 'Bedeutung_Weitere_Deutsch'},
#             {'name': 'Bedeutung_Weitere_Englisch'},
#             {'name': 'Merkbild_Bedeutung'},
#             {'name': 'Merkbild_Kanji'}
#         ],
#         templates=[
#             {
#                 'name': 'Bedeutung Merkbild Karte',
#                 'qfmt': qfmt_meaning,
#                 'afmt': afmt_prefix + '<br/><br/><div class="img_container">{{Merkbild_Bedeutung}}{{Merkbild_Kanji}}</div>' + afmt_postfix
#             }
#         ],
#         css="""
#             .card {
#                 text-align: center;
#                 justify-content: center;
#                 display: flex;
#             }
#             .meaning {
#                 font-weight: bold;
#                 border: 0px solid black;
#                 border-radius: 5px;
#                 padding: 3px;
#             }
#             .radical {
#                 font-weight: bold;
#                 border: 0px solid black;
#                 border-radius: 5px;
#                 padding: 3px;
#                 background-color: #a3ffb3;
#             }
#             .kanji {
#                 font-size: 50px;
#                 padding: 10px;""" +
#             f"background-color: {meaning_kanji_bg};" +
#             """
#             }
#             .additional {
#                 font-size: smaller;
#             }
#             .additional_en {
#                 color: gray;
#             }
#
#             .img_container {
#                 border: 1px solid gray;
#                 position: relative;
#                 width: 300px;
#                 height: 300px;
#             }
#             .image {
#                 position: absolute;
#                 top: 0;
#                 left: 0;
#                 width: 300px;
#                 height: 300px;
#             }
#             .img_container img:nth-child(1) {
#                 animation: fade 6s infinite;
#             }
#             .img_container img:nth-child(2) {
#                 animation: fade2 6s infinite;
#             }
#             @keyframes fade {
#                 0%, 25%, 75%, 100% { opacity: 1; }
#                 50% { opacity: 0; }
#             }
#             @keyframes fade2 {
#                 0%, 100% { opacity: 0; }
#                 25%, 50%, 75% { opacity: 1; }
#             }
#             """
#     )
#
#     mnemonic_reading = genanki.Model(
#         2114858346,
#         'Kyōiku-Kanji Deutsch Lesung Merksatz',
#         fields=[
#             {'name': 'Kanji'},
#             {'name': 'LesungHiragana'},
#             {'name': 'LesungRomaji'},
#             {'name': 'Merksatz'}
#         ],
#         templates=[
#             {
#                 'name': 'Lesung Merksatz Karte',
#                 'qfmt': qfmt_reading,
#                 'afmt': '{{FrontSide}}<br/><br/>{{Merksatz}}'
#             }
#         ],
#         css="""
#             .card {
#                 text-align: center;
#             }
#             .meaning {
#                 font-weight: bold;
#                 border: 0px solid black;
#                 border-radius: 5px;
#                 padding: 3px;
#             }
#             .reading {
#                 font-weight: bold;
#                 border: 0px solid black;
#                 border-radius: 5px;
#                 padding: 3px;
#                 padding-right: 1px;
#                 padding-left: 1px;
#             }
#             .onyomi {
#                 background-color: #ffa3a3;
#             }
#             .kunyomi {
#                 background-color: #a3d9ff;
#             }
#             .kanji {
#                 font-size: 50px;
#                 padding: 10px;""" +
#             f"background-color: {reading_kanji_bg};" +
#             """
#             }
#             """
#     )
#
#     decks = []
#
#     # main deck
#     kanji_kyouiku_deck = genanki.Deck(
#         2114858346,
#         'Kyōiku-Kanji Deutsch')
#     decks.append(kanji_kyouiku_deck)
#
#     # Create a subdeck
#     kanji_kyouiku_first_grade_deck = genanki.Deck(
#         1783656266,
#         'Kyōiku-Kanji Deutsch::Erstes Schuljahr')
#     decks.append(kanji_kyouiku_first_grade_deck)
#
#     for entry in kanji_kyouiku:
#         if not is_done(entry):
#             continue
#
#         if entry['grade'] == 1:
#             if not entry['is_radical']:
#                 note = genanki.Note(
#                     model=mnemonic_meaning,
#                     fields=[
#                         entry['kanji'],
#                         entry['meanings_de'][0].lower(),
#                         ", ".join(entry['meanings_de']),
#                         ", ".join(entry['meanings']),
#                         entry['mnemonic_meaning_de']
#                     ]
#                 )
#                 kanji_kyouiku_first_grade_deck.add_note(note)
#             else:
#                 radical_name = entry['wk_radicals_de'][0]
#                 note = genanki.Note(
#                     model=image_meaning,
#                     fields=[
#                         entry['kanji'],
#                         entry['meanings_de'][0].lower(),
#                         ", ".join(entry['meanings_de']),
#                         ", ".join(entry['meanings']),
#                         f'<img class="image" src="{radical_name}-img.jpg">',
#                         f'<img class="image" src="{radical_name}-kanji.png">'
#                     ]
#                 )
#                 kanji_kyouiku_first_grade_deck.add_note(note)
#
#             # turn reading mnemonic to reading check
#             reading_strs = get_reading_strs(entry)
#
#             reading_hiragana = separator.join([r[0] for r in reading_strs])
#             reading_romaji = separator.join([r[1] for r in reading_strs])
#
#             note = genanki.Note(
#                 model=mnemonic_reading,
#                 fields=[
#                     entry['kanji'],
#                     reading_hiragana,
#                     reading_romaji,
#                     entry['mnemonic_reading_de']
#                 ]
#             )
#             kanji_kyouiku_first_grade_deck.add_note(note)
#
#     # export package
#     package = genanki.Package(decks)
#     package.media_files = []
#     package.media_files.extend(glob.glob('../img/*.jpg'))
#     package.media_files.extend(glob.glob('../img/*.png'))
#
#     output_file = f'../anki/Kyouiku-Kanji-Deutsch_{reading_mode}.apkg'
#     package.write_to_file(output_file)
#
