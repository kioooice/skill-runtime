path = r'D:/02-Projects/vibe/docs/md2img_tiktok.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the last c.save_page() before "PDF 生成完成"
for i in range(len(lines)-1, -1, -1):
    if lines[i].strip() == 'c.save_page()':
        # Check if the next line is "print"
        if i+1 < len(lines) and 'PDF' in lines[i+1]:
            print(f'Found at line {i+1}: {repr(lines[i])} -> {repr(lines[i+1])}')
            # Replace this c.save_page() with showPage + save
            lines[i] = 'c.c.showPage()   # 结束最后一页\n'
            # Also need to add save after it... but we need to insert after
            # Let's replace "print" line to add save
            lines[i+1] = 'c.c.save()\nprint("PDF 生成完成")\n'
            print('Fixed!')
            break

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
