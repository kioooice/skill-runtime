# -*- coding: utf-8 -*-
path = r'D:/02-Projects/vibe/docs/md2img_report.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace curly quotes with escaped straight quotes
content = content.replace('\u201c', '"').replace('\u201d', '"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed!')
