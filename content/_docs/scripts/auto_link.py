# -*- coding: utf-8 -*-
import os
import re
import sys

base = 'knowledge'
ignored_dirs = ['_inbox', '_templates', '_docs']

concepts = {}
filepaths = {}

# 1. Build dictionary of all concepts and aliases
for root, dirs, files in os.walk(base):
    if any(ig in root for ig in ignored_dirs): continue
    for f in files:
        if f.endswith('.md') and f not in ['README.md', 'CLAUDE.md']:
            path = os.path.join(root, f)
            basename = f[:-3]
            concepts[basename.lower()] = basename
            filepaths[path] = basename
            
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    alias_match = re.search(r'^aliases:\s*\[(.*?)\]', content, re.MULTILINE)
                    if alias_match:
                        aliases = [a.strip(' "\'') for a in alias_match.group(1).split(',')]
                        for a in aliases:
                            if a.strip(): concepts[a.strip().lower()] = basename
            except: pass

# Sort concepts by length descending to match longest phrases first
sorted_concept_keys = sorted(concepts.keys(), key=len, reverse=True)
# Filter out too short keys to avoid false positives (e.g. "AI", "Tiền" is 4 chars, so limit > 2)
sorted_concept_keys = [k for k in sorted_concept_keys if len(k) > 2]

modified_count = 0

def process_text_segment(text, current_note_basename):
    for key in sorted_concept_keys:
        canonical = concepts[key]
        if canonical.lower() == current_note_basename.lower(): 
            continue
            
        # Dùng regex cẩn thận với tiếng Việt
        # \b có thể không hoàn hảo với một số ký tự Unicode, ta dùng (?<!\w) và (?!\w)
        pattern = r'(?i)(?<!\w)' + re.escape(key) + r'(?!\w)'
        
        def replacer(match):
            matched_text = match.group(0)
            if matched_text == canonical:
                return f"[[{canonical}]]"
            else:
                return f"[[{canonical}|{matched_text}]]"
                
        # Thay thế nhưng phải bỏ qua nếu nó vô tình nằm sát dấu [ hoặc ]
        # Việc này đã được lo bởi việc split text trước khi đưa vào hàm này.
        text = re.sub(pattern, replacer, text)
    return text

for path, basename in filepaths.items():
    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Tách Frontmatter
        fm_match = re.match(r'^---.*?---\n', content, flags=re.DOTALL)
        if fm_match:
            fm = fm_match.group(0)
            rest = content[len(fm):]
        else:
            fm = ""
            rest = content
            
        # Tách Body và Related
        parts = re.split(r'\n+## Related\s*\n*', rest, maxsplit=1, flags=re.IGNORECASE)
        body = parts[0]
        
        # Tokenize by existing links [[...]] or markdown links [...]() to avoid touching them
        tokens = re.split(r'(\[\[.*?\]\]|\[.*?\]\(.*?\))', body)
        
        new_tokens = []
        for token in tokens:
            if token.startswith('[[') or token.startswith('['):
                new_tokens.append(token)
            else:
                new_tokens.append(process_text_segment(token, basename))
                
        new_body = "".join(new_tokens).strip()
        
        # Tạo lại phần Related từ toàn bộ các link có trong new_body
        all_inline_links = re.findall(r'\[\[(.*?)\]\]', new_body)
        link_targets = set()
        for l in all_inline_links:
            target = l.split('|')[0].strip()
            if target and target != '...':
                link_targets.add(target)
        
        new_related = "\n\n## Related\n"
        if link_targets:
            for target in sorted(link_targets):
                new_related += f"- [[{target}]]\n"
        else:
            new_related += "- [[Khái Niệm Lõi (Atomic Notes)]]\n"
            
        new_content = fm + new_body + new_related
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            modified_count += 1
            if "giáo dục và chính phủ" in basename.lower():
                sys.stdout.buffer.write(f"--> Đã Auto-link inline bài: {basename}\n".encode('utf-8'))
            
    except Exception as e:
        pass

sys.stdout.buffer.write(f"Hoàn tất! Đã nhúng link trực tiếp (Auto-inline link) cho {modified_count} bài viết.\n".encode('utf-8'))
