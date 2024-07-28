# Kanji Data

**This is a fork from https://github.com/davidluzgouveia/kanji-data**

I added to the `kanji-kyouiku.json` more information for German kanji learners.
The preprocessing code is written in Python. The following changes are made.

* Using https://www.kanji-trainer.org/Merksatz/index.html the German meanings are added. See `add_german` function.
* Using https://www.wanikani.com/radicals (downloaded to `wanikani_radicals.html`) we translate radical meaning to German. The translation was done manually with https://deepl.com. The translation can be investigated in `radical-translations.csv`. This is used to create `kanji-kyouiku-de-radicals.json`. There are also radical kanjis added. Since some radicals changed in WaniKani, unused ones are sorted out. See `radicals_check` function.
* Since the Silkworm has missing data, it is removed from the dataset.
* The dataset is a dict. To sort it, it is converted to an array of dicts, see `kanji-kyouiku-de-radicals-array.json`. It is ordered by grade and kanji unicode. See `dict_to_array` function.
* Mnemonic sentences are prepared and manually filled. The keys are `mnemonic_meaning_de` and `mnemonic_reading_de`. It is written to `kanji-kyouiku-de-radicals-array-mnemonics.json`. See `prepare_mnemonics` function.
