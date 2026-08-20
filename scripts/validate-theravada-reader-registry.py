#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'_docs'/'theravada-reader-source-registry.json'
INV=ROOT/'_docs'/'theravada-reference-inventory.json'
def fail(msg):raise SystemExit(f'Theravāda reader registry failed: {msg}')
r=json.loads(REG.read_text());i=json.loads(INV.read_text());sources=r.get('sources') or []
if len(sources)!=i['unique_codes']:fail(f'expected {i["unique_codes"]} sources, got {len(sources)}')
seen=set()
for row in sources:
 code=row.get('code','')
 if code in seen:fail(f'duplicate {code}')
 seen.add(code)
 if not re.fullmatch(r'(DN|MN|SN|AN) \d+(?:\.\d+)?',code):fail(f'bad code {code}')
 for key in ('collection_pali','collection_han_viet','collection_plain_vietnamese','discourse_plain_vietnamese_title','url','plain_summary'):
  if not isinstance(row.get(key),str) or not row[key].strip():fail(f'{code} missing {key}')
 if row.get('title_verification_status') not in {'verified-existing-source','verified-suttacentral','verified-descriptive'}:fail(f'{code} unverified title')
 if row.get('discourse_han_viet_title') and not row.get('han_viet_verification_source'):fail(f'{code} Hán-Việt title lacks verification source')
 if row.get('used_in_lessons')!=i['all_codes'][code]:fail(f'{code} lesson usage drift')
print(json.dumps({'status':'pass','sources':len(sources),'han_viet_titles':sum(bool(x.get('discourse_han_viet_title')) for x in sources)},ensure_ascii=False))
