#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_docs'/'theravada-batch4-scripture-audit.json'
cache={}
def fetch(rid):
 if rid not in cache:
  u=f'https://suttacentral.net/api/bilarasuttas/{rid}/sujato?lang=en'
  with urllib.request.urlopen(u,timeout=30) as r: cache[rid]=(u,r.status,json.loads(r.read()))
 return cache[rid]
def expand(order,spec):
 if '–' not in spec:return [spec]
 a,b=spec.split('–')
 if ':' not in b:b=a.split(':',1)[0]+':'+b
 i=order.index(a);j=order.index(b);return order[i:j+1]
rows=[]
for n in range(23,29):
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));lines=p.read_text().splitlines();i=0
 while i<len(lines):
  m=re.match(r'> \*\*Pāli — ([A-Z]{2,})\s*(\d+(?:\.\d+)?), .*?`(.+?)`\*\*$',lines[i])
  if not m:i+=1;continue
  rid=m.group(1).lower()+m.group(2);url,status,d=fetch(rid);order=d['keys_order'];root=d['root_text']
  specs=re.findall(r'`([^`]+)`',lines[i]);keys=[]
  for spec in specs:keys.extend(expand(order,spec))
  j=i+1
  while j<len(lines) and not lines[j].startswith('> *'):j+=1
  if j>=len(lines):raise SystemExit(f'missing Pali line {p}:{i+1}')
  expected=' '.join(root[k].strip() for k in keys)
  actual=lines[j][3:-1]
  rows.append({'lesson':n,'file':p.name,'discourse':rid,'segment_ids':keys,'url':url,'http_status':status,'exact_match':actual==expected,'expected_sha256':hashlib.sha256(expected.encode()).hexdigest(),'actual_sha256':hashlib.sha256(actual.encode()).hexdigest()})
  i=j+1
report={'schema':'theravada-scripture-audit.v1','scope':'lessons-23-28','blocks':len(rows),'passed':sum(x['exact_match'] for x in rows),'all_pass':all(x['exact_match'] for x in rows),'rows':rows}
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('blocks','passed','all_pass')},ensure_ascii=False))
raise SystemExit(0 if report['all_pass'] else 1)
