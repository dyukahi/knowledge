#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'_docs'/'theravada-reader-rewrite-progress.json').read_text())
BARE_RE=re.compile(r'\b(?:DN|MN|SN|AN)\s+\d+(?:\.\d+)?\b')
def fail(msg):raise SystemExit(f'Theravāda reader rewrite failed: {msg}')
total=0
for n in P.get('completed_lessons',[]):
 f=next((ROOT/'theravada').glob(f'{n:02d}*.md'));parts=f.read_text().split('---',2);body=parts[2] if len(parts)>2 else f.read_text();lines=body.splitlines();cards=[]
 for i,line in enumerate(lines):
  if line.startswith('> [!quote]'):
   j=i+1;block=[]
   while j<len(lines) and lines[j].startswith('>'):block.append(lines[j]);j+=1
   if any(x.startswith('> <small>Nguồn kiểm chứng:') for x in block):cards.append((i+1,block))
 if not cards:fail(f'lesson {n}: no narrative quote cards')
 for lineno,block in cards:
  text='\n'.join(block);pali=sum(x.startswith('> **Pāli**') for x in block);translations=sum(x.startswith('> **Dịch Việt**') or x.startswith('> **Dịch Việt rút gọn**') for x in block);sources=sum(x.startswith('> <small>Nguồn kiểm chứng:') for x in block)
  if (pali,translations,sources)!=(1,1,1):fail(f'lesson {n}:{lineno} malformed narrative card')
  if 'REVIEW_REQUIRED' in text:fail(f'lesson {n}:{lineno} review marker')
  if '**Dịch Việt**' in text and '…' in text.split('**Dịch Việt**',1)[1]:fail(f'lesson {n}:{lineno} abbreviated translation mislabeled')
  if any(label in text for label in ('Tên dễ hiểu:','Nằm ở đâu:','Đoạn này nói gì:','Nói nôm na:','Vì sao dùng ở đây:','Tên truyền thống/Hán-Việt:')):fail(f'lesson {n}:{lineno} form-style metadata remains')
 for lineno,line in enumerate(lines,1):
  if not BARE_RE.search(line):continue
  allowed=('Nguồn kiểm chứng:' in line or line.startswith('- [') or 'suttacentral.net/' in line or line.startswith('Đọc trước:'))
  if not allowed:fail(f'lesson {n}:{lineno} bare scripture code')
 total+=len(cards)
print(json.dumps({'status':'pass','contract':'narrative-quote-v1','completed_lessons':len(P.get('completed_lessons',[])),'narrative_cards':total},ensure_ascii=False))
