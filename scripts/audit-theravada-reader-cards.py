#!/usr/bin/env python3
from __future__ import annotations
import hashlib,html,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROGRESS=json.loads((ROOT/'_docs'/'theravada-reader-rewrite-progress.json').read_text())
def clean(s):
 s=re.sub(r'\s*\(<b>.*?</b>\)','',s);return re.sub(r'<[^>]+>','',html.unescape(s)).strip()
def expand(order,rid,spec):
 spec=spec.strip().replace(';','')
 if ':' not in spec:spec=f'{rid}:{spec}'
 if '–' not in spec:return [spec]
 a,b=spec.split('–');b=b if ':' in b else a.split(':',1)[0]+':'+b;return order[order.index(a):order.index(b)+1]
rows=[];cache={}
for n in PROGRESS['completed_lessons']:
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));ls=p.read_text().splitlines()
 for i,line in enumerate(ls):
  if not line.startswith('> **Mã kiểm chứng:**'):continue
  m=re.search(r'`((?:DN|MN|SN|AN)\s+\d+(?:\.\d+)?)`',line);assert m,(p,i,line);code=m.group(1);rid=code.replace(' ','').lower()
  if rid not in cache:
   u=f'https://suttacentral.net/api/bilarasuttas/{rid}/sujato?lang=en';d=json.loads(urllib.request.urlopen(u,timeout=30).read());cache[rid]=(u,d)
  u,d=cache[rid];order=d['keys_order'];root=d['root_text'];tokens=[x for x in re.findall(r'`([^`]+)`',line) if x!=code and (':' in x or re.fullmatch(r'\d+(?:\.\d+)*(?:–\d+(?:\.\d+)*)?',x))]
  if not tokens:
   tail=line.split('`,',1)[-1];tokens=re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)+(?:–\d+(?:\.\d+)*)?',tail)
  keys=[]
  for token in tokens:
   for part in re.split(r'[,;]\s*',token):
    if part:keys.extend(expand(order,rid,part))
  assert keys,(p,i,line)
  j=i+1
  while j<len(ls) and not ls[j].startswith('> **Pāli gốc:**'):j+=1
  assert j<len(ls);actual=ls[j].split(':**',1)[1].strip();
  if actual.startswith('*') and actual.endswith('*'):actual=actual[1:-1]
  expected=' '.join(clean(root[k]) for k in keys)
  rows.append({'lesson':n,'code':code,'segments':keys,'url':u,'raw_sha256':hashlib.sha256(' '.join(root[k].strip() for k in keys).encode()).hexdigest(),'normalized_sha256':hashlib.sha256(expected.encode()).hexdigest(),'actual_sha256':hashlib.sha256(actual.encode()).hexdigest(),'exact_match':actual==expected})
report={'schema':'theravada-reader-card-exact-audit.v1','completed_lessons':PROGRESS['completed_lessons'],'cards':len(rows),'passed':sum(r['exact_match'] for r in rows),'all_pass':all(r['exact_match'] for r in rows),'rows':rows};(ROOT/'_docs'/'theravada-reader-card-exact-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('completed_lessons','cards','passed','all_pass')},ensure_ascii=False));raise SystemExit(0 if report['all_pass'] else 1)
