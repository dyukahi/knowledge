#!/usr/bin/env python3
from __future__ import annotations
import hashlib,html,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_docs'/'theravada-batch6-scripture-audit.json'
cache={}
def fetch(rid):
 if rid not in cache:
  u=f'https://suttacentral.net/api/bilarasuttas/{rid}/sujato?lang=en'
  with urllib.request.urlopen(u,timeout=30) as r:cache[rid]=(u,r.status,json.loads(r.read()))
 return cache[rid]
def stripped(s):
 s = re.sub(r'\s*\(<b>.*?</b>\)', '', s)
 return re.sub(r'<[^>]+>', '', html.unescape(s)).strip()
def expand(order,spec):
 if '–' not in spec:return [spec]
 a,b=spec.split('–');b=b if ':' in b else a.split(':',1)[0]+':'+b
 i=order.index(a);j=order.index(b);return order[i:j+1]
rows=[]
for n in range(33,37):
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));lines=p.read_text().splitlines();i=0
 while i<len(lines):
  if not lines[i].startswith('> **Pāli —'):i+=1;continue
  specs=re.findall(r'`([^`]+)`',lines[i]);
  if not specs:raise SystemExit(f'Pāli label lacks exact IDs: {p}:{i+1}')
  rid=specs[0].split(':',1)[0];url,status,d=fetch(rid);order=d['keys_order'];root=d['root_text'];keys=[]
  for spec in specs:keys.extend(expand(order,spec))
  j=i+1
  while j<len(lines) and not lines[j].startswith('> *'):j+=1
  if j>=len(lines):raise SystemExit(f'missing Pāli line: {p}:{i+1}')
  raw=' '.join(root[k].strip() for k in keys);expected=' '.join(stripped(root[k]) for k in keys);actual=lines[j][3:-1]
  rows.append({'lesson':n,'file':p.name,'discourse':rid,'segment_ids':keys,'url':url,'http_status':status,'normalization':'HTML entities decoded; editorial HTML tags stripped; segment order preserved; surrounding whitespace stripped; one space joins segments','raw_sha256':hashlib.sha256(raw.encode()).hexdigest(),'normalized_sha256':hashlib.sha256(expected.encode()).hexdigest(),'actual_sha256':hashlib.sha256(actual.encode()).hexdigest(),'exact_match':actual==expected})
  i=j+1
expected_counts={33:3,34:3,35:2,36:2};counts={n:sum(r['lesson']==n for r in rows) for n in expected_counts}
report={'schema':'theravada-scripture-audit.v1','scope':'lessons-33-36','expected_counts':expected_counts,'counts':counts,'blocks':len(rows),'passed':sum(r['exact_match'] for r in rows),'all_pass':counts==expected_counts and all(r['exact_match'] for r in rows),'rows':rows}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('counts','blocks','passed','all_pass')},ensure_ascii=False));raise SystemExit(0 if report['all_pass'] else 1)
