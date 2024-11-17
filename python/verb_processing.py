import json

import genanki


def verbs_make_anki():
    with open('../kanji-kyouiku-verbs-wip.json', 'rt', encoding='utf-8') as file:
        kyouiku_verbs = json.load(file)

    with open('card.css', 'rt') as file:
        css = file.read().strip()

    qfmt = '''
    <span class="kanji">{{Vokabel}}</span>
    <br/>
    <br/>
    {{type:Antwort}}
    '''

    afmt = '''
    {{FrontSide}}
    <br/>
    {{Merksatz}}
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
            {'name': 'Merksatz'},

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
                '<br/>' + verb['mnemonic'] + '<br/>' if verb['mnemonic_done'] else '',

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




# def verbs_scanner():
#     with open('../kanji-kyouiku-common-words.json', 'rt', encoding='utf-8') as file:
#         common_words = json.load(file)
#
#         common_words_dict = defaultdict(list)
#
#         # emulate missing frequencies
#         for word in common_words:
#             if word['freq'] is None:
#                 word['freq'] = {
#                     '2015_rank': 20000,
#                     '2022_rank': 20000
#                 }
#
#             # and set rank
#             word['freq']['rank'] = word['freq'].get('2015_rank', 0) + word['freq'].get('2022_rank', 0)
#
#             common_words_dict[word['word']].append(word)
#
#     with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
#         kanji_kyouiku = json.load(file)
#
#         kanji_kyouiku_dict = {}
#         kanji_kyouiku_list = []
#
#         for entry in kanji_kyouiku:
#             kanji_kyouiku_dict[entry['kanji']] = {
#                 'meanings_de': entry['meanings_de'],
#                 'reading_dist': entry.get('reading_dist'),
#                 'reading_strs': get_reading_strs(entry)
#             }
#
#             kanji_kyouiku_list.append(entry['kanji'])
#
#     html = requests.get('https://www.japaneseverbconjugator.com/JVerbList.asp')
#     soup = BeautifulSoup(html.content, 'html.parser')
#
#     table = soup.find_all('table')[1]
#
#     kyouiku_verbs = []
#
#     error_count = 0
#
#     i = 1
#     easy_count = 0
#     for tr in table.find_all('tr'):
#         tds = tr.find_all('td')
#
#         if len(tds) < 4:
#             continue
#
#         romaji = tds[0].get_text().strip()
#
#         furigana = tds[1].find('span', class_="furigana").get_text().strip()
#         # fix for 生える
#         furigana = furigana.replace(',', '')
#         kanji_text_elem = tds[1].find('div', class_="JScript")
#
#         if kanji_text_elem is None:
#             error_count += 1
#             continue
#
#         kanji_text = kanji_text_elem.get_text().strip()
#
#         if len(kanji_text) == 0 or len(furigana) == 0:
#             error_count += 1
#             continue
#
#         meaning = tds[2].get_text().strip()
#
#         #ms = []
#         #for m in meaning.split(','):
#         #    m = m.strip()
#         #    m_de = translate_and_cache(m)
#         #    ms.append(m_de)
#         # meaning_de = ', '.join(ms)
#
#         meaning_de = translate_and_cache(meaning)
#         mode = tds[3].get_text().strip()
#
#         # fix
#         if kanji_text == '加わる':
#             # Godan, see https://jisho.org/search/%E5%8A%A0%E3%82%8F%E3%82%8B
#             mode = '1'
#
#         # need negative plain form for correct conjugation later
#         if mode == '1':
#             # Godan
#             kanji_text_neg = u_to_a(kanji_text) + 'ない'
#             furigana_neg = u_to_a(furigana) + 'ない'
#
#         elif mode == '2':
#             # Ichidan
#             kanji_text_neg = kanji_text[:-1] + 'ない'
#             furigana_neg = furigana[:-1] + 'ない'
#
#         else:
#             raise Exception("mode not found: " + mode + ", " + kanji_text)
#
#         #better kanji detection
#         extracted_kanjis = extract_kanji(kanji_text)
#         kyouiku_kanjis = []
#         reading_learned = False
#         for char in extracted_kanjis:
#             if char in kanji_kyouiku_dict:
#                 readings = kanji_kyouiku_dict[char]['reading_strs']
#                 kyouiku_kanjis.append((char, kanji_kyouiku_dict[char]['meanings_de'], readings))
#                 for hira, roma in readings:
#                     reading_learned |= furigana.startswith(hira)
#
#         matching_words = common_words_dict.get(kanji_text, [])
#
#         kyouiku_friendly = len(extracted_kanjis) > 0 and len(extracted_kanjis) == len(kyouiku_kanjis)
#
#         kyouiku_index = -1
#         if kyouiku_friendly:
#             kyouiku_index = kanji_kyouiku_list.index(kyouiku_kanjis[0][0])
#
#         # 422 having all info
#         # 249 with a match
#         #  12 with two   or more matches
#         #   0 with three or more matches
#         #  13 have two kanjis
#         #  78 reading is learned (and kyouiku_friendly), can be higher later
#         # 280 kyouiku_friendly (66%, 2/3)
#
#
#         #if kyouiku_friendly and reading_learned:
#         # if len(matching_words) > 0:
#         if kyouiku_friendly:
#             easy_count += 1
#
#         kanji_part, kanji_reading = remove_until_diff(kanji_text, furigana)
#         kanji_reading_romaji = hiragana_to_romaji(kanji_reading)
#
#         main_meaning_de = meaning_de.split(',')[0].strip()
#         # Go-Dan = female
#         # Ichi-Dan = male
#         mode_decides_gender = 'Sie' if mode == '1' else 'Er'
#
#         mnemonic = f"{mode_decides_gender}  {main_meaning_de}  <span class='reading kunyomi' data-hiragana='{kanji_reading}'>{kanji_reading_romaji}</span> <span class='hiragana'>({kanji_reading})</span>"
#
#         kyouiku_verb = OrderedDict([
#             ('romaji', romaji),
#             ('furigana', furigana),
#             ('furigana_neg', furigana_neg),
#             ('kanji_part', kanji_part),
#             ('kanji_reading', kanji_reading),
#             ('kanji_reading_romaji', kanji_reading_romaji),
#             ('word', kanji_text),
#             ('word_neg', kanji_text_neg),
#             ('mnemonic', mnemonic),
#             ('mnemonic_done', False),
#             ('kanjis', kyouiku_kanjis),
#             ('kyouiku_index', kyouiku_index),
#             ('meaning', meaning),
#             ('meaning_de', meaning_de),
#             ('main_meaning_de', main_meaning_de),
#             ('mode', mode),
#             ('kyouiku_friendly', kyouiku_friendly),
#             ('reading_learned', reading_learned),
#             ('common_words', matching_words)
#         ])
#         kyouiku_verbs.append(kyouiku_verb)
#
#         #print(i, romaji, furigana, kanji_text, kanjis, meaning, meaning_de, mode, kyouiku_friendly, reading_learned, len(matching_words), kyouiku_index, sep=' | ')
#         #for word in matching_words:
#         #    print('\t', word)
#         #i += 1
#
#     #print(easy_count)
#
#     # 108
#     # print(error_count)
#
#     kyouiku_verbs.sort(key=lambda x: (len(x['kanjis']), x['kyouiku_index']))
#
#     #print(len(kyouiku_verbs))
#
#     kyouiku_verbs_filter = [verb for verb in kyouiku_verbs if verb['kyouiku_friendly']]
#
#     with open('../kanji-kyouiku-verbs.json', 'wt', encoding='utf-8') as file:
#         json.dump(kyouiku_verbs_filter, file, indent=4, ensure_ascii=False)
