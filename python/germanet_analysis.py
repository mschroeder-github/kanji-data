import json
import os
from collections import defaultdict

from bs4 import BeautifulSoup
from tqdm import tqdm

from scipy.spatial.distance import cosine

def germanet_categories():


    germanet_list = defaultdict(list)
    germanet_set = defaultdict(set)

    all_categories = []

    filenames = os.listdir('../germanet')
    filenames.sort()
    # print(filenames)

    for filename in tqdm(filenames):

        category, _ = os.path.splitext(filename)

        # adj, nomen, verben might not matter
        category = category.split('.')[1]

        all_categories.append(category)

        with open(os.path.join('../germanet', filename), 'r') as file:
            soup = BeautifulSoup(file, 'xml')

        orth_forms = soup.find_all('orthForm')

        for orth in orth_forms:
            #germanet_list[orth.text.lower()].append(category)
            germanet_set[orth.text.lower()].add(category)


    print(len(all_categories), ' categories')
    print(len(germanet_list), ' germanet list entries')
    print(len(germanet_set), ' germanet set entries')

    with open('../kanji-kyouiku-de-radicals-array-mnemonics-wip.json', 'rt', encoding='utf-8') as file:
        kanji_kyouiku = json.load(file)

    germanet = germanet_set

    for entry in kanji_kyouiku:
        embedding = [0.0] * len(all_categories)

        # ['Buch', 'Ursprung', 'Zählwort f. lange Dinge', 'wahr']
        # "wahr" will get 1/4
        for i, meaning in enumerate(entry['meanings_de']):
            rank = i + 1
            meaning = meaning.lower()
            for cat in germanet[meaning]:
                embedding[all_categories.index(cat)] += 1 # 1 / rank

            # only the first meaning
            break

        total = sum([e for e in embedding])
        categories = [all_categories[i] for i, e in enumerate(embedding) if e > 0]

        if total > 0:
            # normalize
            embedding = [(e / total) for e in embedding]

            germanet_dict = {
                "categories": categories,
                "embedding": embedding
            }
            entry['germanet'] = germanet_dict

    kanji_kyouiku_done = [entry for entry in kanji_kyouiku if entry['mnemonic_reading_de_done'] and 'germanet' in entry]

    print(len(kanji_kyouiku_done), 'done')

    next_index = 0

    kanji_kyouiku_sorted = []

    while kanji_kyouiku_done:
        a = kanji_kyouiku_done.pop(next_index)
        kanji_kyouiku_sorted.append(a)

        if len(kanji_kyouiku_done) == 0:
            break

        b = min(kanji_kyouiku_done, key=lambda x: cosine(a['germanet']['embedding'], x['germanet']['embedding']))

        next_index = kanji_kyouiku_done.index(b)

    for entry in kanji_kyouiku_sorted:
        print(entry['meanings_de']) #, entry['germanet']['categories'], entry['germanet']['embedding'])
