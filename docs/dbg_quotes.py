# -*- coding: utf-8 -*-
f = open(r'D:/02-Projects/vibe/docs/md2img_cn.py', 'r', encoding='utf-8')
lines = f.readlines()
f.close()
line = lines[142]
print('LINE 143:')
for i, ch in enumerate(line):
    if ord(ch) in [0x22, 0x27, 0x201C, 0x201D, 0x300C, 0x300D, 0xFF02]:
        print(f'  pos={i} U+{ord(ch):04X} char={repr(ch)}')
