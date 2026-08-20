#!/usr/bin/env python3
from __future__ import annotations
import hashlib,html,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=json.loads((ROOT/'_docs'/'theravada-reader-rewrite-progress.json').read_text());REG=json.loads((ROOT/'_docs'/'theravada-reader-source-registry.json').read_text())['sources'];BY_URL={r['canonical_url'].rstrip('/'):r for r in REG}
def clean(s):s=re.sub(r'\s*\(<b>.*?</b>\)','',s);return re.sub(r'<[^>]+>','',html.unescape(s)).strip()
def expand(order,rid,spec):
 spec=spec.strip().strip('`').replace(';','');
 if ':' not in spec:spec=f'{rid}:{spec}'
 if '–' not in spec:return [spec]
 a,b=spec.split('–',1);b=b if ':' in b else a.split(':',1)[0]+':'+b;return order[order.index(a):order.index(b)+1]
rows=[];cache={}
for n in P.get('completed_lessons',[]):
 f=next((ROOT/'theravada').glob(f'{n:02d}*.md'));ls=f.read_text().splitlines()
 for i,line in enumerate(ls):
  if not line.startswith('> <small>Nguồn kiểm chứng:'):continue
  u=re.search(r'href="([^"]+)"',line).group(1).rstrip('/');row=BY_URL[u];rid=row['work_id']
  if rid not in cache:
   api=f'https://suttacentral.net/api/bilarasuttas/{rid}/sujato?lang=en';d=json.loads(urllib.request.urlopen(api,timeout=30).read());cache[rid]=(api,d)
  api,d=cache[rid];order=d['keys_order'];root=d['root_text'];plain=clean(line);explicit=re.findall(rf'{re.escape(rid)}:\d+(?:\.\d+)*(?:–(?:{re.escape(rid)}:)?\d+(?:\.\d+)*)?',plain)
  tokens=explicit or re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)+(?:–\d+(?:\.\d+)*)?',plain.split(',',1)[-1]);keys=[]
  for token in tokens:keys.extend(expand(order,rid,token))
  if not keys:raise RuntimeError(f'no locator {f}:{i+1}')
  # Pāli line belongs to the same quote block immediately above source line.
  j=i-1
  while j>=0 and not ls[j].startswith('> **Pāli**'):j-=1
  if j<0:raise RuntimeError(f'no Pāli heading {f}:{i+1}')
  k=j+1
  while k<i and not (ls[k].startswith('> *') and ls[k].endswith('*')):k+=1
  actual=ls[k][3:-1];expected=' '.join(clean(root[x]) for x in keys)
  rows.append({'lesson':n,'source_key':row['source_key'],'work_id':rid,'segments':keys,'url':api,'raw_sha256':hashlib.sha256(' '.join(root[x].strip() for x in keys).encode()).hexdigest(),'normalized_sha256':hashlib.sha256(expected.encode()).hexdigest(),'actual_sha256':hashlib.sha256(actual.encode()).hexdigest(),'exact_match':actual==expected})
report={'schema':'theravada-reader-card-exact-audit.v2','contract':'narrative-quote-v1','completed_lessons':P.get('completed_lessons',[]),'cards':len(rows),'passed':sum(r['exact_match'] for r in rows),'all_pass':all(r['exact_match'] for r in rows),'rows':rows};(ROOT/'_docs'/'theravada-reader-card-exact-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('completed_lessons','cards','passed','all_pass')},ensure_ascii=False));raise SystemExit(0 if report['all_pass'] else 1)
