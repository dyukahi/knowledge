# -*- coding: utf-8 -*-
import os
import re
import sys
from collections import Counter

base = 'knowledge'
ignored_dirs = ['_inbox', '_templates', '_docs']

# 1. Delete empty files
deleted_files = []
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.md') and f not in ['README.md', 'CLAUDE.md']:
            path = os.path.join(root, f)
            try:
                size = os.path.getsize(path)
                if size == 0:
                    os.remove(path)
                    deleted_files.append(f)
                    continue
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                if not content.strip():
                    os.remove(path)
                    deleted_files.append(f)
            except:
                pass

# 2. Health check
total_files = 0
missing_frontmatter = []
missing_related = []
broken_filenames = []

all_notes = set()
all_links = []
file_outgoing = {}

for root, dirs, files in os.walk(base):
    if any(ig in root for ig in ignored_dirs): continue
    for f in files:
        if not f.endswith('.md') or f in ['README.md', 'CLAUDE.md']: continue
        total_files += 1
        basename = f[:-3]
        all_notes.add(basename.lower())
        
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8') as file: content = file.read()
            
            if not content.lstrip().startswith('---'): missing_frontmatter.append(f)
            if '## Related' not in content: missing_related.append(f)
            
            # Extract aliases
            alias_match = re.search(r'^aliases:\s*\[(.*?)\]', content, re.MULTILINE)
            if alias_match:
                aliases = [a.strip(' "\'') for a in alias_match.group(1).split(',')]
                for a in aliases:
                    if a: all_notes.add(a.lower())

            links = re.findall(r'\[\[(.*?)\]\]', content)
            valid_links = [l.split('|')[0].strip() for l in links if l.strip() and l.strip() != '...']
            file_outgoing[f] = valid_links
            all_links.extend(valid_links)
        except Exception as e:
            if '?' in f or '' in f:
                broken_filenames.append(f)

broken_links = set(l for l in all_links if l.lower() not in all_notes)
orphans = [f for f, links in file_outgoing.items() if len(links) == 0 and not any(f[:-3].lower() == l.lower() for l in all_links)]

def out(text):
    sys.stdout.buffer.write((text + '\n').encode('utf-8'))

out(f"=== KẾT QUẢ DỌN DẸP ===")
out(f"Đã xóa {len(deleted_files)} file trống: {', '.join(deleted_files)}")

out(f"\n=== BÁO CÁO HEALTH CHECK TOÀN DIỆN ===")
out(f"Tổng số ghi chú: {total_files}")
out(f"Lỗi Encoding (Tên file): {len(broken_filenames)}")
out(f"Thiếu Frontmatter: {len(missing_frontmatter)}")
out(f"Thiếu ## Related: {len(missing_related)}")
out(f"Note mồ côi (Orphan): {len(orphans)}")
out(f"Link mờ/Gaps (Chưa có bài): {len(broken_links)}")

if broken_links:
    counts = Counter(l for l in all_links if l.lower() not in all_notes)
    out("\n[Top 5 Lỗ hổng tri thức cần viết tiếp]")
    for link, count in counts.most_common(5):
        out(f"- [[{link}]] ({count} lần)")
