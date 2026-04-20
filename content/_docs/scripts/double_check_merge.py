# -*- coding: utf-8 -*-
import os
import re
import sys

base = 'knowledge'
ignored_dirs = ['_inbox', '_templates', '_docs']

notes = []
for root, dirs, files in os.walk(base):
    if any(ig in root for ig in ignored_dirs): continue
    for f in files:
        if f.endswith('.md') and f not in ['README.md', 'CLAUDE.md']:
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                notes.append({
                    'f': f, 
                    'basename': f[:-3], 
                    'path': path, 
                    'content': content,
                    'len': len(content)
                })
            except: pass

def norm(s):
    # Xóa nội dung trong ngoặc đơn
    s = re.sub(r'\(.*?\)', '', s)
    # Bỏ các ký tự đặc biệt, dấu gạch nối
    s = s.replace('-', ' ').replace('_', ' ')
    # Xóa sạch khoảng trắng, đưa về chữ thường
    s = re.sub(r'\s+', '', s).lower()
    return s

clusters = {}
for n in notes:
    nn = norm(n['basename'])
    if nn not in clusters: clusters[nn] = []
    clusters[nn].append(n)

# Kéo các file trùng alias vào chung 1 cluster
for n in notes:
    am = re.search(r'^aliases:\s*\[(.*?)\]', n['content'], re.MULTILINE)
    if am:
        aliases = [a.strip(' "\'') for a in am.group(1).split(',')]
        for a in aliases:
            na = norm(a)
            if na and na in clusters:
                nn = norm(n['basename'])
                if nn != na:
                    clusters[na].extend(clusters[nn])
                    clusters[nn] = [] # Làm rỗng cụm cũ

merged_reports = []
for key, items in clusters.items():
    if not items: continue
    
    # Loại bỏ trùng lặp nếu có do quá trình kéo cluster
    unique_items = {}
    for it in items:
        unique_items[it['path']] = it
    items = list(unique_items.values())
    
    if len(items) > 1:
        # Ưu tiên bài có status: refined, sau đó là độ dài
        def score(x):
            s = 1 if 'status: refined' in x['content'] else 0
            return (s, x['len'])
            
        items.sort(key=score, reverse=True)
        main = items[0]
        subs = items[1:]
        
        aliases_to_add = []
        content_to_add = ""
        
        for sub in subs:
            aliases_to_add.append(sub['basename'])
            # Chỉ hút nội dung nếu bài sub không phải là stub và có dung lượng kha khá
            if 'status: stub' not in sub['content'] and len(sub['content']) > 200:
                clean_sub = re.sub(r'^---.*?---', '', sub['content'], flags=re.MULTILINE|re.DOTALL).strip()
                content_to_add += f"\n\n## [Nội dung gộp từ bài trùng: {sub['basename']}]\n\n" + clean_sub
            
            # Xóa bài trùng
            if os.path.exists(sub['path']):
                os.remove(sub['path'])
            
        # Thêm alias vào bài chính
        main_c = main['content']
        if aliases_to_add:
            exist_match = re.search(r'^aliases:\s*\[(.*?)\]', main_c, re.MULTILINE)
            if exist_match:
                exist_str = exist_match.group(1)
                exist_list = [a.strip(' "\'') for a in exist_str.split(',')]
                new_aliases = list(set(exist_list + aliases_to_add))
                new_alias_str = 'aliases: [' + ', '.join(f'"{a}"' for a in new_aliases if a) + ']'
                main_c = main_c.replace(exist_match.group(0), new_alias_str)
            else:
                new_alias_str = 'aliases: [' + ', '.join(f'"{a}"' for a in aliases_to_add) + ']'
                main_c = re.sub(r'^title: (.*?)$', r'title: \1\n' + new_alias_str, main_c, flags=re.MULTILINE)
        
        if content_to_add:
            main_c += content_to_add
            
        with open(main['path'], 'w', encoding='utf-8') as f:
            f.write(main_c)
            
        merged_reports.append(f"- Gộp {len(subs)} bài vào '{main['basename']}' (Đã xóa: {', '.join(aliases_to_add)})")

def out(text):
    sys.stdout.buffer.write((text + '\n').encode('utf-8'))

out("=== BÁO CÁO DOUBLE CHECK & MERGE ===")
if merged_reports:
    for r in merged_reports:
        out(r)
else:
    out("Hệ thống sạch sẽ tuyệt đối, không phát hiện bài trùng.")
