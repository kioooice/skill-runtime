# -*- coding: utf-8 -*-
path = r'D:/02-Projects/vibe/docs/md2img_cn.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
# Replace Chinese curly quotes with single quotes (they appear inside Python string literals)
content = content.replace(chr(0x201C), "'").replace(chr(0x201D), "'")
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('done: curly quotes replaced with single quotes')
