inotifywait -m -e modify kanji-kyouiku-de-radicals-array-mnemonics-wip.json | while read; do sh to_docs.sh; done
