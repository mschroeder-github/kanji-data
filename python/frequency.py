import csv
import gzip
from collections import defaultdict

import requests
from bs4 import BeautifulSoup


def frequency_crawler():

    links = [
        #('2013', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese/Wikipedia2013'),
        #('2013', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese10001-20000'),
        ('2015', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2015_10000'),
        ('2015', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2015_10001-20000'),
        ('2022', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2022_10000'),
        ('2022', 'https://en.m.wiktionary.org/wiki/Wiktionary:Frequency_lists/Japanese2022_10001-20000')
    ]

    japanese_basic_words_1000 = requests.get('https://en.m.wiktionary.org/wiki/Appendix:1000_Japanese_basic_words').content
    soup = BeautifulSoup(japanese_basic_words_1000, 'html.parser')
    japanese_basic_words_1000 = set()
    for anchor in soup.find_all('a'):
        japanese_basic_words_1000.add(anchor.get_text())

    word_dict = defaultdict(dict)

    for name, link in links:

        content = requests.get(link).content

        soup = BeautifulSoup(content, 'html.parser')

        print(link)

        tbl = soup.find('table')
        for tr in tbl.find_all('tr')[1:]:
            tds = tr.find_all('td')

            rank = int(tds[0].get_text())
            freq = int(tds[1].get_text())
            word = tds[2].get_text()

            word_dict[word][f'{name}_freq'] = freq
            word_dict[word][f'{name}_rank'] = rank
            word_dict[word][f'in_1000_basic_words'] = word in japanese_basic_words_1000

    #max_2015_rank = max([v['2015_rank'] for v in word_dict.values() if '2015_rank' in v])
    #max_2022_rank = max([v['2022_rank'] for v in word_dict.values() if '2022_rank' in v])

    min_2015_freq = min([v['2015_freq'] for v in word_dict.values() if '2015_freq' in v])
    max_2015_freq = max([v['2015_freq'] for v in word_dict.values() if '2015_freq' in v])

    min_2022_freq = min([v['2022_freq'] for v in word_dict.values() if '2022_freq' in v])
    max_2022_freq = max([v['2022_freq'] for v in word_dict.values() if '2022_freq' in v])

    # this is always 9999 (because 10,000)
    #print('max_2015_rank', max_2015_rank)
    #print('max_2022_rank', max_2022_rank)
    #print('2015 freq range', min_2015_freq, max_2015_freq)
    #print('2022 freq range', min_2022_freq, max_2022_freq)

    for v in word_dict.values():
        if '2015_rank' in v:
            v['2015_rank_prop'] = (9999 - v['2015_rank']) / 9999

        if '2022_rank' in v:
            v['2022_rank_prop'] = (9999 - v['2022_rank']) / 9999

        v['min_2015_freq'] = min_2015_freq
        v['max_2015_freq'] = max_2015_freq
        v['min_2022_freq'] = min_2022_freq
        v['max_2022_freq'] = max_2022_freq

        if '2015_freq' in v:
            v['2015_rel_freq'] = (v['2015_freq'] - min_2015_freq) / (max_2015_freq - min_2015_freq)

        if '2022_freq' in v:
            v['2022_rel_freq'] = (v['2022_freq'] - min_2022_freq) / (max_2022_freq - min_2022_freq)

    print(len(word_dict), 'in word_dict')
    print('example:', '可能', word_dict['可能'])
    print('example:', '人', word_dict['人'])

    return word_dict


def subtitle_freq_load():
    freq_dict = {}
    # subtitle based frequency
    with gzip.open('../word_freq_report.txt.gz', 'rt', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for no, row in enumerate(reader, start=1):
            row.insert(0, no)

            if row[2] in freq_dict:
                raise Exception('duplicate')

            freq_dict[row[2]] = row

    return freq_dict