#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARK='<!-- vault-voice-opening:v1 -->'
rows=[];seen=set();bare=[]
for n in range(1,37):
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));lines=p.read_text().splitlines();
 if MARK not in lines:raise SystemExit(f'vault voice missing lesson {n}')
 i=lines.index(MARK);opening=[]
 for line in lines[i+1:]:
  if line.startswith('## '):break
  if line.strip():opening.append(line.strip())
 text='\n'.join(opening);words=len(re.findall(r'\w+',text,re.UNICODE));
 if words<45 or words>180:raise SystemExit(f'opening length lesson {n}: {words}')
 digest=hashlib.sha256(text.encode()).hexdigest()
 if digest in seen:raise SystemExit(f'duplicate opening lesson {n}')
 seen.add(digest);rows.append({'lesson':n,'words':words,'sha256':digest})
 body=False
 for number,line in enumerate(lines,1):
  if number>1 and line=='---':body=True;continue
  if not body or line.startswith('> <small>Nguồn kiểm chứng:'):continue
  for m in re.finditer(r'(?<![/\w])(DN|MN|SN|AN)\s+\d+(?:\.\d+)?',line):bare.append((n,number,m.group(0)))
if bare:raise SystemExit(f'reader-facing bare codes: {bare[:10]}')
review=json.loads((ROOT/'_docs/theravada-reader-pilot-semantic-review.json').read_text());exact=json.loads((ROOT/'_docs/theravada-reader-card-exact-audit.json').read_text());registry=json.loads((ROOT/'_docs/theravada-reader-source-registry.json').read_text())
if review['cards']!=113 or review['passed']!=113:raise SystemExit('semantic review count drift')
if exact['cards']!=113 or exact['passed']!=113 or not exact['all_pass']:raise SystemExit('exact card count drift')
if len(registry['sources'])!=67:raise SystemExit('registry count drift')
required={4:['attadīpā viharatha','an8.53'],9:['sn45.2','appamādena sampādethā'],23:['dn31','an5.161']}
for n,tokens in required.items():
 text=next((ROOT/'theravada').glob(f'{n:02d}*.md')).read_text().casefold()
 for token in tokens:
  if token.casefold() not in text:raise SystemExit(f'missing foundational passage lesson {n}: {token}')
report={'schema':'theravada-vault-voice-audit.v1','lessons':36,'openings':rows,'unique_openings':len(seen),'reader_facing_bare_codes':0,'cards':113,'semantic_passed':113,'exact_pali_passed':113,'registry_sources':67,'foundational_passage_lessons':[4,9,23],'all_pass':True};(ROOT/'_docs/theravada-vault-voice-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('lessons','unique_openings','reader_facing_bare_codes','cards','semantic_passed','exact_pali_passed','registry_sources','all_pass')},ensure_ascii=False))
