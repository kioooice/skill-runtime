# -*- coding: utf-8 -*-
# 只修复 md2img_cn.py 中真正有问题的行（ASCII " 充当中文引号）
path = r'D:/02-Projects/vibe/docs/md2img_cn.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 重新写入原始文件（fix_ascii_quotes 已经破坏了一些内容）
# 先从 skill-runtime-project-report.md 重新生成 Python 脚本

# 但这次我们用更简单的方式：
# 把所有 Python 字符串中的中文引号风格的 "xxx" 改为 'xxx'
# 更安全的方法：直接扫描含中文的行，把连续的中文+引号+中文 模式里的引号换掉

lines = content.split('\n')
fixed = []
for lineno, line in enumerate(lines, 1):
    # 跳过注释行和明显不是问题的行
    if line.strip().startswith('#') or 'Paragraph' not in line:
        fixed.append(line)
        continue
    # 在包含 Paragraph 的行里，找 "xxx" 这种中文引号模式
    new_line = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            # 判断前后是否是CJK字符
            prev_cjk = i > 0 and ('\u4e00' <= line[i-1] <= '\u9fff' or
                                   '\u3000' <= line[i-1] <= '\u303f')
            next_cjk = i+1 < len(line) and ('\u4e00' <= line[i+1] <= '\u9fff' or
                                            '\u3000' <= line[i+1] <= '\u303f')
            if prev_cjk or next_cjk:
                new_line.append("'")
            else:
                new_line.append('"')
        else:
            new_line.append(ch)
        i += 1
    fixed.append(''.join(new_line))

with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed))
print('done, fixed Chinese quote chars')
