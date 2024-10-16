inotifywait -m -e modify kanji-kyouiku-de-radicals-array-mnemonics-wip.json kanji-kyouiku-verbs-wip.json | while read; do sh to_docs.sh; sh to_docs_verbs.sh; done
