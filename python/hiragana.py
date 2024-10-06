# Dictionary to map Hiragana characters and combinations to their ASCII equivalents
hiragana_to_ascii = {
    'あ': 'a', 'い': 'i', 'う': 'u', 'え': 'e', 'お': 'o',
    'か': 'ka', 'き': 'ki', 'く': 'ku', 'け': 'ke', 'こ': 'ko',
    'さ': 'sa', 'し': 'shi', 'す': 'su', 'せ': 'se', 'そ': 'so',
    'た': 'ta', 'ち': 'chi', 'つ': 'tsu', 'て': 'te', 'と': 'to',
    'な': 'na', 'に': 'ni', 'ぬ': 'nu', 'ね': 'ne', 'の': 'no',
    'は': 'ha', 'ひ': 'hi', 'ふ': 'fu', 'へ': 'he', 'ほ': 'ho',
    'ま': 'ma', 'み': 'mi', 'む': 'mu', 'め': 'me', 'も': 'mo',
    'や': 'ya', 'ゆ': 'yu', 'よ': 'yo',
    'ら': 'ra', 'り': 'ri', 'る': 'ru', 'れ': 're', 'ろ': 'ro',
    'わ': 'wa', 'を': 'wo', 'ん': 'n',
    'が': 'ga', 'ぎ': 'gi', 'ぐ': 'gu', 'げ': 'ge', 'ご': 'go',
    'ざ': 'za', 'じ': 'ji', 'ず': 'zu', 'ぜ': 'ze', 'ぞ': 'zo',
    'だ': 'da', 'ぢ': 'ji', 'づ': 'zu', 'で': 'de', 'ど': 'do',
    'ば': 'ba', 'び': 'bi', 'ぶ': 'bu', 'べ': 'be', 'ぼ': 'bo',
    'ぱ': 'pa', 'ぴ': 'pi', 'ぷ': 'pu', 'ぺ': 'pe', 'ぽ': 'po',
    'きゃ': 'kya', 'きゅ': 'kyu', 'きょ': 'kyo',
    'しゃ': 'sha', 'しゅ': 'shu', 'しょ': 'sho',
    'ちゃ': 'cha', 'ちゅ': 'chu', 'ちょ': 'cho',
    'にゃ': 'nya', 'にゅ': 'nyu', 'にょ': 'nyo',
    'ひゃ': 'hya', 'ひゅ': 'hyu', 'ひょ': 'hyo',
    'みゃ': 'mya', 'みゅ': 'myu', 'みょ': 'myo',
    'りゃ': 'rya', 'りゅ': 'ryu', 'りょ': 'ryo',
    'ぎゃ': 'gya', 'ぎゅ': 'gyu', 'ぎょ': 'gyo',
    'じゃ': 'ja', 'じゅ': 'ju', 'じょ': 'jo',
    'びゃ': 'bya', 'びゅ': 'byu', 'びょ': 'byo',
    'ぴゃ': 'pya', 'ぴゅ': 'pyu', 'ぴょ': 'pyo'
}

def hiragana_to_romaji(hiragana_text):
    romaji_text = ''
    small_tsu = False
    i = 0
    while i < len(hiragana_text):
        if i + 1 < len(hiragana_text) and hiragana_text[i:i+2] in hiragana_to_ascii:
            word = hiragana_to_ascii[hiragana_text[i:i+2]]
            if small_tsu:
                romaji_text += word[0]
                small_tsu = False
            romaji_text += word
            i += 2
        elif hiragana_text[i] == 'っ':
            small_tsu = True
            i += 1
        elif hiragana_text[i] in hiragana_to_ascii:
            word = hiragana_to_ascii[hiragana_text[i]]
            if small_tsu:
                romaji_text += word[0]
                small_tsu = False
            romaji_text += word
            i += 1
        else:
            # romaji_text += hiragana_text[i]
            i += 1

    return romaji_text


u_to_a_dict = {
    'う': 'わ',
    'く': 'か',
    'す': 'さ',
    'つ': 'た',
    'ぬ': 'な',
    'む': 'ま',
    'む': 'ま',
    'ゆ': 'や',
    'る': 'ら',
    'ぐ': 'が',
    'ず': 'ざ',
    'づ': 'だ',
    'ぶ': 'ば',
    'ぷ': 'ぱ'
}

def u_to_a(text):
    last = text[-1]
    val = u_to_a_dict.get(last)
    if val is None:
        raise Exception(f"{last} not found")
    return text[:-1] + val