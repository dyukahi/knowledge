#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'_docs'/'theravada-reader-source-registry.json'
INV=ROOT/'_docs'/'theravada-reference-inventory.json'
def fail(msg):raise SystemExit(f'Theravāda reader registry failed: {msg}')
r=json.loads(REG.read_text());i=json.loads(INV.read_text());sources=r.get('sources') or []
if len(sources)<i['unique_codes']:fail(f'expected at least {i["unique_codes"]} sources, got {len(sources)}')
seen=set()
for row in sources:
 code=row.get('source_key') or row.get('code','')
 if code in seen:fail(f'duplicate {code}')
 seen.add(code)
 if row.get('source_type') not in {'sutta','vinaya','abhidhamma'}:fail(f'{code} missing source_type')
 if not isinstance(row.get('work_id'),str) or not row['work_id']:fail(f'{code} missing work_id')
 for key in ('collection_pali','collection_han_viet','collection_plain_vietnamese','discourse_plain_vietnamese_title','url','plain_summary'):
  if not isinstance(row.get(key),str) or not row[key].strip():fail(f'{code} missing {key}')
 if row.get('title_verification_status') not in {'verified-existing-source','verified-suttacentral','verified-descriptive'}:fail(f'{code} unverified title')
 if row.get('discourse_han_viet_title') and not row.get('han_viet_verification_source'):fail(f'{code} Hán-Việt title lacks verification source')
 if code in i['all_codes'] and row.get('used_in_lessons')!=i['all_codes'][code]:fail(f'{code} lesson usage drift')
if not set(i['all_codes']).issubset(seen):fail('legacy registry coverage missing')
vinaya={x['source_key']:x for x in sources if x['source_type']=='vinaya'}
if vinaya:
 if set(vinaya)!={'VINAYA pli-tv-kd21','VINAYA pli-tv-kd22'}:fail('unexpected Vinaya adapter set')
 for key,row in vinaya.items():
  label='Cullavagga XI' if key.endswith('kd21') else 'Cullavagga XII'
  actual=[]
  for lesson in range(1,37):
   article=next((ROOT/'theravada').glob(f'{lesson:02d}*.md'))
   pattern=r'\bCullavagga XI(?!I)\b' if label.endswith('XI') else r'\bCullavagga XII\b'
   if re.search(pattern,article.read_text()):actual.append(lesson)
  if row.get('used_in_lessons')!=actual:fail(f'{key} lesson usage drift: {actual}')
 for key,row in vinaya.items():
  locators=row.get('locator_inventory') or []
  if not locators:fail(f'{key} locator inventory missing')
  for loc in locators:
   if not loc.get('segment_ids') or len(loc.get('raw_sha256',''))!=64 or len(loc.get('normalized_sha256',''))!=64:fail(f'{key} locator hash evidence incomplete')
print(json.dumps({'status':'pass','sources':len(sources),'families':dict(__import__('collections').Counter(x['source_type'] for x in sources)),'han_viet_titles':sum(bool(x.get('discourse_han_viet_title')) for x in sources)},ensure_ascii=False))
