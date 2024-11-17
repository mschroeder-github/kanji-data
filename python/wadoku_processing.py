import json
from collections import defaultdict

from tqdm import tqdm

from helper import print_element


def collect_wadoku():
    tree = ET.parse('../wadoku-xml-20240707/wadoku.xml')
    root = tree.getroot()

    ns = {'': 'http://www.wadoku.de/xml/entry'}

    wadoku_vocabs = []

    for entry in tqdm(root.findall('entry', ns)):
        try:
            vocab = {}

            entry_id = entry.get('id')
            link = f"https://www.wadoku.de/entry/view/{entry_id}"

            vocab['words'] = []
            for form in entry.findall('form', ns):
                orths = form.findall("orth", ns)
                for orth in orths:
                    if orth.text not in vocab['words']:
                        vocab['words'].append(orth.text)

            #if vocab['words'] == ['一生']:
            #    print_element(entry)
            #    a = 0

            hira = entry.find("form/reading/hira", ns)
            if hira is not None:
                vocab['reading'] = hira.text

            vocab['meanings_de'] = []

            #if len(senses) == 0:
            #    print_element(entry)
            #    raise Exception('no senses found for ' + vocab['words'])

            for sense in entry.findall('sense', ns):
                transes = list(sense.findall('trans', ns))
                if len(transes) == 0:
                    transes = []
                    for subsense in sense.findall('sense', ns):
                        transes.extend(subsense.findall('trans', ns))

                if len(transes) == 0:
                    continue
                    # raise Exception('no translations found for ' + str(vocab['words']))

                trans_list = []
                for trans in transes:
                    tr = trans.find('tr', ns)
                    if tr is None:
                        tr = trans.find('title', ns)

                    #if tr is None:
                    #    print_element(trans)
                    #    continue

                    tr_text = ''
                    for child in tr:
                        if child.get('hasPrecedingSpace'):
                            tr_text += ' '

                        txt = ' '.join(child.itertext())
                        tr_text += txt

                        if child.get('hasFollowingSpace'):
                            tr_text += ' '

                    trans_list.append(tr_text)

                vocab['meanings_de'].append(trans_list)

            # print(json.dumps(vocab, indent=2, ensure_ascii=False))
            wadoku_vocabs.append(vocab)

        except Exception as e:
            print_element(entry)
            raise e

    with open('../wadoku-vocabs.json', 'wt', encoding='utf-8') as file:
        json.dump(wadoku_vocabs, file, indent=4, ensure_ascii=False)



def wadoku_load():
    with open('../wadoku-vocabs.json', 'rt', encoding='utf-8') as file:
        wadoku_vocabs = json.load(file)

        wadoku_vocabs_dict = defaultdict(list)
        for entry in wadoku_vocabs:
            for word in entry['words']:
                wadoku_vocabs_dict[word + entry['reading']].append(entry)

        wadoku_vocabs_word_dict = defaultdict(list)
        for entry in wadoku_vocabs:
            for word in entry['words']:
                wadoku_vocabs_word_dict[word].append(entry)

    return wadoku_vocabs_dict, wadoku_vocabs_word_dict