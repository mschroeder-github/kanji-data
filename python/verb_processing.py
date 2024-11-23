import json
import os

import genanki

from hiragana import hiragana_to_romaji


def verbs_make_anki(num_learned_kanjis=50, reading_mode="Umschrift", separator=" "):
    os.makedirs('../anki', exist_ok=True)

    with open('../jisho_verbs-wip.json', 'rt', encoding='utf-8') as file:
        jisho_verbs = json.load(file)

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
    <br/>
    {{Merksatz}}
    <br/>
    <br/>
    <div style="text-align: start;">
    Plain Positive: {{Lesung_Hiragana}} | Plain Negative: {{Lesung_Hiragana_Negation}}<br/>
    <br/>
    {{Bedeutungen_Deutsch}}<br/>
    <br/>
    {{Bedeutungen_Englisch}}<br/>
    <br/>
    <hr/>
    <br/>
    {{Lesung_Teile}}<br/>
    <br/>
    {{Kanji_Bedeutungen}}<br/>
    <br/>
    <hr/>
    <br/>
    Typ: {{Dan}}-dan, Rang: {{Rang}}, Lesung-Einfachheit: {{Kanji_Lesung_Gelernt}}, Kanji-Level: {{Gelernte_Kanjis_Benötigt}} 
    </div>
    '''

    deck = genanki.Deck(
        1210461573,
        'Unterrichtsschriftzeichen - Verben'
    )

    model = genanki.Model(
        1417794174,
        'Verb',
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
            {'name': 'Lesung_Teile'},
            {'name': 'Kanji_Bedeutungen'},

            {'name': 'Dan'},
            {'name': 'Kanji_Lesung_Gelernt'},
            {'name': 'Gelernte_Kanjis_Benötigt'},
            {'name': 'Rang'}
        ],
        templates=[
            {
                'name': 'Verb Karte',
                'qfmt': qfmt,
                'afmt': afmt
            }
        ],
        css=css
    )

    # filter jisho_verbs based on kanji level
    jisho_verbs = [v for v in jisho_verbs if v['max_kanji_index'] <= num_learned_kanjis]
    print(f"{len(jisho_verbs)} verbs <= kanji level {num_learned_kanjis}")

    # sort by rank
    jisho_verbs.sort(key=lambda x: x['freq']['rank'])

    i = 0
    for verb in jisho_verbs:
        if not verb['kyouiku_friendly'] or not verb['mnemonic_de_done']:
            continue

        guid = genanki.guid_for(verb['word'] + verb['reading'])

        romaji = hiragana_to_romaji(verb['reading'])
        romaji_neg = hiragana_to_romaji(verb['reading_neg'])

        l = []
        for m in verb['meanings_de']:
            l.append(f"<li>{'; '.join(m)}</li>")
        meanings_de_txt = '\n'.join(l)

        l = []
        for m in verb['meanings']:
            l.append(f"<li>{m[0]} ({m[1]})</li>")
        meanings_txt = '\n'.join(l)

        l = []
        for m in verb['word_parts']:
            l.append(f"{m[0]}={m[1]}")
        word_parts_txt = ', '.join(l)

        answer = f"{verb['main_meaning_de']} {romaji_neg}".lower()

        l = []
        for m in verb['kanji_meanings_de']:
            l.append(f"{m[0]}={';'.join(m[1])}")
        kanji_meanings_de_txt = ', '.join(l)

        note = genanki.Note(
            model=model,
            guid=guid,
            fields=[
                verb['word'],
                answer,
                verb['mnemonic_de'],

                meanings_de_txt,
                meanings_txt,
                verb['word_neg'],

                verb['reading'],
                romaji,

                verb['reading_neg'],
                romaji_neg,

                word_parts_txt,
                kanji_meanings_de_txt,

                verb['dan'],
                str(verb['kanji_reading_score']),
                str(verb['max_kanji_index']),
                str(verb['freq']['rank'])
            ]
        )

        deck.add_note(note)
        i += 1

    package = genanki.Package([deck])
    output_file = f'../anki/Unterrichtsschriftzeichen_Verben-Level_{num_learned_kanjis:04}-{reading_mode}_Abfrage.apkg'
    package.write_to_file(output_file)

    print(f'{i} verbs written to {output_file}')

def verbs_make_anki_lvls(max=50):
    for lvl in range(50, max+1, 50):
        verbs_make_anki(num_learned_kanjis=lvl)

