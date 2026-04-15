# -*- coding: utf-8 -*-
import os
import re
import sys

base = 'knowledge'
ignored_dirs = ['_inbox', '_templates', '_docs']

note_words = {}
note_paths = {}
stopwords = set('và là của các có trong những một không với cho này như được từ để lại hay hoặc mà đã đang sẽ về tại theo'.split())

for root, dirs, files in os.walk(base):
    if any(ig in root for ig in ignored_dirs): continue
    for f in files:
        if f.endswith('.md') and f not in ['README.md', 'CLAUDE.md']:
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                words = set(w for w in re.findall(r'\b\w+\b', content.lower()) if w not in stopwords and len(w) > 2)
                note_words[f[:-3]] = words
                note_paths[f[:-3]] = path
            except: pass

modified_count = 0

for name, path in note_paths.items():
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tách phần Body và phần Related cũ
        parts = re.split(r'\n+## Related\s*\n*', content, maxsplit=1, flags=re.IGNORECASE)
        body = parts[0].strip()
        related_part = parts[1] if len(parts) > 1 else ""
        
        # Bóc tách TẤT CẢ các link có trong Body (kể cả link đang có)
        inline_links = [l.split('|')[0].strip() for l in re.findall(r'\[\[(.*?)\]\]', body)]
        inline_links = [l for l in inline_links if l and l != '...']
        
        # Bóc tách TẤT CẢ các link đang có trong Related cũ
        related_links = [l.split('|')[0].strip() for l in re.findall(r'\[\[(.*?)\]\]', related_part)]
        related_links = [l for l in related_links if l and l != '...']
        
        # Gộp chung, loại bỏ trùng lặp (không phân biệt hoa thường)
        all_target_links = []
        seen = set()
        
        for l in related_links + inline_links:
            ll = l.lower()
            if ll not in seen:
                seen.add(ll)
                all_target_links.append(l)
                
        # Nếu tổng số link < 2, dùng AI similarity để tìm thêm bài liên quan nhét vào
        if len(all_target_links) < 2:
            my_words = note_words[name]
            scores = []
            for other_name, other_words in note_words.items():
                if other_name.lower() == name.lower(): continue
                score = len(my_words.intersection(other_words))
                scores.append((score, other_name))
            scores.sort(reverse=True)
            for score, other_name in scores:
                if other_name.lower() not in seen and score > 0:
                    all_target_links.append(other_name)
                    seen.add(other_name.lower())
                if len(all_target_links) >= 4:  # Max 4 links added this way
                    break
                    
        # Xây dựng lại block ## Related mới
        new_related = "\n\n## Related\n"
        if not all_target_links:
            new_related += "- [[Khái Niệm Lõi (Atomic Notes)]]\n"
        else:
            for l in all_target_links:
                new_related += f"- [[{l}]]\n"
                
        new_content = body + new_related
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified_count += 1
            if "Điều mà nền giáo dục" in name or "không dạy bạn" in name.lower():
                sys.stdout.buffer.write(f"--> Đã fix bài: {name}\n".encode('utf-8'))
    except Exception as e:
        pass

sys.stdout.buffer.write(f"\nĐã quét SÂU toàn bộ hệ thống.\nCập nhật lại ## Related cho {modified_count} bài viết.\n".encode('utf-8'))
