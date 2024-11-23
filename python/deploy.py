import os
import re
import shutil
import subprocess
from string import Template
from datetime import datetime

def deploy_anki_to_mdbook(mdbook_src_path):
    trg_dir = os.path.join(mdbook_src_path, 'anki')

    shutil.copytree('../anki', trg_dir, dirs_exist_ok=True)
    print('anki directory copied')

    with open('lernmaterialien.md', 'rt') as file:
        content = file.read()
        tmpl = Template(content)

    current_date = datetime.now()
    german_date = current_date.strftime("%d.%m.%Y")

    words_list = []
    verbs_list = []
    for f in os.listdir(trg_dir):
        if f.startswith('Unterrichtsschriftzeichen_Gebraeuchliche_Woerter'):
            words_list.append(f)

        if f.startswith('Unterrichtsschriftzeichen_Verben'):
            verbs_list.append(f)

    def get_name(f):
        nums = re.findall(r'\d+', os.path.basename(f))
        return f'Level {int(nums[0])}'

    words = '\n'.join([f'* [{get_name(f)}](anki/{os.path.basename(f)})' for f in sorted(words_list)])
    verbs = '\n'.join([f'* [{get_name(f)}](anki/{os.path.basename(f)})' for f in sorted(verbs_list)])

    content = tmpl.substitute(date=german_date, words=words, verbs=verbs)

    with open(os.path.join(mdbook_src_path, 'lernmaterialien.md'), 'wt') as file:
        file.write(content)

    print('lernmaterialien.md written')

def deploy_mdbook_to_server():
    result = subprocess.run(['sh', '../scripts/upload_mdbook_to_strato.sh'], capture_output=True, text=True)
    print(result.stdout)

def deploy_all(mdbook_src_path):
    deploy_anki_to_mdbook(mdbook_src_path)
    deploy_mdbook_to_server()
