# Kanji Data

**This is a fork from https://github.com/davidluzgouveia/kanji-data**

I added to the `kanji-kyouiku.json` more information for German kanji learners.
The preprocessing code is written in Python. The following changes are made.

* Using https://www.kanji-trainer.org/Merksatz/index.html the German meanings are added. See `add_german` function.
* Using https://www.wanikani.com/radicals (downloaded to `wanikani_radicals.html`) we translate radical meaning to German. The translation was done manually with https://deepl.com. The translation can be investigated in `radical-translations.csv`. This is used to create `kanji-kyouiku-de-radicals.json`. There are also radical kanjis added. Since some radicals changed in WaniKani, unused ones are sorted out. See `radicals_check` function.
* Since the Silkworm has missing data, it is removed from the dataset.
* The dataset is a dict. To sort it, it is converted to an array of dicts, see `kanji-kyouiku-de-radicals-array.json`. It is ordered by grade and kanji unicode. See `dict_to_array` function.
* Mnemonic sentences are prepared and manually filled. The keys are `mnemonic_meaning_de` and `mnemonic_reading_de`. It is written to `kanji-kyouiku-de-radicals-array-mnemonics.json`. See `prepare_mnemonics` function.
* The `kanji-kyouiku-de-radicals-array-mnemonics-wip.json` is the Work-In-Progress (WIP) file that is filled manually. The `watch_copy_to_docs.sh` is used to copy it to `docs`.
* In `docs` folder is `kyouiku-de.html` which shows a table of the kanjis and mnemonics.

### Example

An entry in `kanji-kyouiku-de-radicals-array-mnemonics-wip.json` has the following structure:


```json
{
    "strokes": 3,
    "grade": 1,
    "freq": 97,
    "jlpt_old": 4,
    "jlpt_new": 5,
    "meanings": [
        "Below",
        "Down",
        "Descend",
        "Give",
        "Low",
        "Inferior"
    ],
    "readings_on": [
        "か",
        "げ"
    ],
    "readings_kun": [
        "した",
        "しも",
        "もと",
        "さ.げる",
        "さ.がる",
        "くだ.る",
        "くだ.り",
        "くだ.す",
        "-くだ.す",
        "くだ.さる",
        "お.ろす",
        "お.りる"
    ],
    "wk_level": 1,
    "wk_meanings": [
        "Below",
        "^Down",
        "^Under",
        "^Beneath"
    ],
    "wk_readings_on": [
        "か",
        "げ"
    ],
    "wk_readings_kun": [
        "!した",
        "!さ",
        "!くだ",
        "!お"
    ],
    "wk_radicals": [
        "Ground",
        "Toe"
    ],
    "meanings_de": [
        "unten",
        "abwärts",
        "hinabsteigen"
    ],
    "wk_radicals_new": [
        "Ground",
        "Toe"
    ],
    "wk_radicals_missing": [],
    "wk_radicals_de": [
        "Boden",
        "Zehe"
    ],
    "wk_radicals_kanji": [
        "一",
        "ト"
    ],
    "kanji": "下",
    "kanji_ord": 19979,
    "is_radical": false,
    "mnemonic_meaning_de": "Im <span class='radical' data-kanji='一'>Boden</span> <span class='radical_kanji'>(一)</span> steckt meine <span class='radical' data-kanji='ト'>Zehe</span> <span class='radical_kanji'>(ト)</span> und zeigt nach <span class='meaning' data-kanji='下'>unten</span> <span class='meaning_kanji_meaning'>(下)</span>.",
    "mnemonic_meaning_de_done": true,
    "mnemonic_reading_de": "Haare hängen nach <span class='meaning' data-kanji='下'>unten</span> <span class='meaning_kanji_reading'>(下)</span>, also mit <span class='reading onyomi' data-hiragana='か'>Ka</span>mm <span class='hiragana'>(か)</span> und <span class='reading onyomi' data-hiragana='げ'>Ge</span>l <span class='hiragana'>(げ)</span> stylen.",
    "mnemonic_reading_de_done": true
}
```

**Radical -> Meaning Mnmemonic**

A German sentence that combines the radicals to form the meaning.

> Im <span class='radical' data-kanji='一'>Boden</span> <span class='radical_kanji'>(一)</span> steckt meine <span class='radical' data-kanji='ト'>Zehe</span> <span class='radical_kanji'>(ト)</span> und zeigt nach <span class='meaning' data-kanji='下'>unten</span> <span class='meaning_kanji_meaning'>(下)</span>.

**Meaning -> Reading Mnmemonic**

A German sentence that uses markup to emphasize how to read the kanji.
<style>
.reading { font-weight: bold; }
</style>

> Haare hängen nach <span class='meaning' data-kanji='下'>unten</span> <span class='meaning_kanji_reading'>(下)</span>, also mit <span class='reading onyomi' data-hiragana='か'>Ka</span>mm <span class='hiragana'>(か)</span> und <span class='reading onyomi' data-hiragana='げ'>Ge</span>l <span class='hiragana'>(げ)</span> stylen.
