# -*- coding: utf-8 -*-
import os
import re
import datetime

base = 'knowledge'
ignored_dirs = ['_inbox', '_templates', '_docs']
date_str = datetime.datetime.now().strftime('%Y-%m-%d')

notes = {}
all_links = {}

# 1. Đọc hệ thống hiện tại
for root, dirs, files in os.walk(base):
    if any(ig in root for ig in ignored_dirs): continue
    for f in files:
        if f.endswith('.md') and f not in ['README.md', 'CLAUDE.md']:
            basename = f[:-3]
            notes[basename.lower()] = (basename, os.path.join(root, f), root)
            
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as file:
                    content = file.read()
                    alias_match = re.search(r'^aliases:\s*\[(.*?)\]', content, re.MULTILINE)
                    if alias_match:
                        aliases = [a.strip(' "\'') for a in alias_match.group(1).split(',')]
                        for a in aliases:
                            if a: notes[a.lower()] = (basename, os.path.join(root, f), root)
            except: pass

# 2. Thu thập link và tìm 3 bài thiếu Related
missing_related = []
for root, dirs, files in os.walk(base):
    if any(ig in root for ig in ignored_dirs): continue
    for f in files:
        if f.endswith('.md') and f not in ['README.md', 'CLAUDE.md']:
            path = os.path.join(root, f)
            basename = f[:-3]
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                if '## Related' not in content:
                    missing_related.append((path, basename))
                    
                links = re.findall(r'\[\[(.*?)\]\]', content)
                for l in links:
                    target = l.split('|')[0].strip()
                    if target and target != '...':
                        target_low = target.lower()
                        if target_low not in all_links:
                            all_links[target_low] = {'name': target, 'sources': set()}
                        all_links[target_low]['sources'].add(basename)
            except: pass

# 3. Bổ sung Related cho 3 bài còn thiếu
fixed_related_count = 0
for path, basename in missing_related:
    try:
        with open(path, 'a', encoding='utf-8') as file:
            file.write('\n\n## Related\n- [[Khái Niệm Lõi (Atomic Notes)]] - Ghi chú hệ thống.\n')
        fixed_related_count += 1
    except: pass

# 4. Điền 113 Gaps (Tạo Stub Notes)
created_count = 0
for target_low, data in all_links.items():
    if target_low not in notes:
        target_name = data['name']
        sources = list(data['sources'])
        
        # Xếp file stub vào cùng thư mục với bài viết đã nhắc đến nó
        source_folder = base
        if sources:
            source_basename = sources[0]
            if source_basename.lower() in notes:
                source_folder = notes[source_basename.lower()][2]
                
        clean_filename = re.sub(r'[\\/*?:"<>|]', '', target_name) + '.md'
        new_path = os.path.join(source_folder, clean_filename)
        
        if not os.path.exists(new_path):
            related_links = "\n".join([f"- [[{s}]] - Bài viết nguồn nhắc đến khái niệm này." for s in sources[:5]])
            stub_content = f"""---
title: "{target_name}"
date: {date_str}
tags: ["stub", "cần-mở-rộng"]
status: stub
---

## Khái niệm: {target_name}
(Đây là một ghi chú chờ - Stub Note. Khái niệm này được phát hiện trong quá trình quét hệ thống và đang chờ được tổng hợp, phát triển chi tiết).

## Related
{related_links}
"""
            try:
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write(stub_content)
                created_count += 1
            except: pass

import sys
sys.stdout.buffer.write(f"Đã bổ sung ## Related cho {fixed_related_count} bài.\n".encode('utf-8'))
sys.stdout.buffer.write(f"Đã lấp đầy toàn bộ mạng lưới: Tạo {created_count} ghi chú (Stub Notes) cho các link mờ.\n".encode('utf-8'))
