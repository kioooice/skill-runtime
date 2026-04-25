# -*- coding: utf-8 -*-
path = r'D:/02-Projects/vibe/docs/md2img_cn.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
# Replace Chinese/curly quotes with single quotes first
content = content.replace(chr(0x201C), "'").replace(chr(0x201D), "'")
# Also replace ASCII double quotes inside strings that look like Chinese quotes
# The pattern: Chinese text "Chinese text" followed by Chinese text
# Strategy: replace ASCII " used as Chinese quotation marks with ' or with \"
# More targeted: replace pattern "中文" where " is surrounded by non-ASCII chars
import re

# Split into lines, fix each line that has Python string literals with embedded quotes
lines = content.split('\n')
fixed_lines = []
for line in lines:
    # Find the pattern: inside a Python string, replace " used as Chinese quotes with '
    # We look for " that appears after Chinese characters (non-ASCII) and before Chinese chars
    # Simple heuristic: if a " is between two non-ASCII chars, it's a Chinese quote
    new_line = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            # Check if this could be a Chinese quote
            prev_ascii = i > 0 and (line[i-1] > '\u4e00' and line[i-1] <= '\u9fff')
            next_ascii = i+1 < len(line) and (line[i+1] > '\u4e00' and line[i+1] <= '\u9fff')
            if prev_ascii or next_ascii:
                # This is likely a Chinese quote, replace with '
                new_line.append("'")
            else:
                new_line.append('"')
        else:
            new_line.append(ch)
        i += 1
    fixed_lines.append(''.join(new_line))

with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))
print('done: fixed Chinese quotes in Python strings')
