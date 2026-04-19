# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    'app_monitor/templates/species-gallery.html',
    'app_monitor/templates/species.html',
    'app_monitor/templates/species-detail.html',
]

yu_char = '\u9n6c'   # 鹬 (yù)
weng_char = '\u99df'  # 鹟 (wēng)

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if '鹤鹟' in content:
        new_content = content.replace('鹤鹟', '鹤鹬')
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed: {fpath} (鹤鹟 -> 鹤鹬)')
    elif '鹤鹬' in content:
        print(f'Already correct: {fpath}')
    else:
        print(f'Not found: {fpath}')
