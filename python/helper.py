import re
import xml.etree.ElementTree as ET
from xml.dom import minidom

from bs4 import BeautifulSoup

from hiragana import hiragana_to_romaji


def get_reading_strs(entry):
    soup = BeautifulSoup(entry['mnemonic_reading_de'], 'html.parser')
    readings = soup.find_all("span", class_="reading")
    reading_strs = []
    for r in readings:
        hiragana = r['data-hiragana']
        romaji = hiragana_to_romaji(hiragana)
        reading_strs.append((hiragana, romaji))
    return reading_strs


def remove_brackets(text):
    return re.sub(r'\(.*?\)', '', text)


def extract_kanji(text):
    kanji_pattern = r'[\u4e00-\u9faf]'
    kanji_characters = re.findall(kanji_pattern, text)
    return list(set(kanji_characters))


def print_element(entry):
    xml_str = ET.tostring(entry, 'utf-8')
    parsed_xml = minidom.parseString(xml_str)
    print(parsed_xml.toprettyxml(indent="  "))


def is_done(entry):
    return entry['mnemonic_reading_de_done'] and (entry['mnemonic_meaning_de_done'] or entry.get('has_radical_img'))


def remove_until_diff(str1, str2):
    while str1 and str2 and str1[-1] == str2[-1]:
        str1 = str1[:-1]
        str2 = str2[:-1]
    return str1, str2