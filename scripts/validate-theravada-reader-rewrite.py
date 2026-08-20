#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROGRESS=ROOT/'_docs'/'theravada-reader-rewrite-progress.json'
BARE_RE=re.compile(r'\b(?:DN|MN|SN|AN)\s+\d+(?:\.\d+)?\b')
def fail(msg):raise SystemExit(f'Theravāda reader rewrite failed: {msg}')
p=json.loads(PROGRESS.read_text());completed=p.get('completed_lessons') or [];required=p['required_source_card_fields'];translation_fields=p['translation_field_alternatives'];review_marker=p['review_marker']
for n in completed:
 f=next((ROOT/'theravada').glob(f'{n:02d}*.md'));s=f.read_text();parts=s.split('---',2);body=parts[2] if len(parts)>2 else s
 pali=body.count('> **Pāli gốc:**')
 cards=body.count('> [!quote] Nguồn Kinh dễ hiểu')
 if not pali or cards!=pali:fail(f'lesson {n}: cards={cards}, Pāli={pali}')
 for field in required:
  if body.count(f'> **{field}:**')<cards:fail(f'lesson {n}: missing field {field}')
 if sum(body.count(f'> **{field}:**') for field in translation_fields)!=cards:
  fail(f'lesson {n}: each card needs exactly one truthful translation label')
 if review_marker in body:fail(f'lesson {n}: unresolved semantic review marker')
 # Bare codes are allowed only in source-card/source-list lines, not explanatory prose or headings.
 for lineno,line in enumerate(body.splitlines(),1):
  if not BARE_RE.search(line):continue
  allowed=(line.startswith('> **Mã kiểm chứng:**') or line.startswith('- [') or 'suttacentral.net/' in line or line.startswith('Đọc trước:'))
  if not allowed:fail(f'lesson {n}:{lineno} bare scripture code: {line[:120]}')
print(json.dumps({'status':'pass','completed_lessons':len(completed),'source_cards':sum(next((ROOT/'theravada').glob(f'{n:02d}*.md')).read_text().count('> [!quote] Nguồn Kinh dễ hiểu') for n in completed)},ensure_ascii=False))
