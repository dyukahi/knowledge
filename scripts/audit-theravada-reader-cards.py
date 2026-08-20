#!/usr/bin/env python3
from __future__ import annotations
import hashlib,html,json,re,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def clean(s):
 s=re.sub(r'\s*\(<b>.*?</b>\)','',s);return ' '.join(re.sub(r'<[^>]+>','',html.unescape(s)).strip().split())
def expand(order,rid,spec):
 spec=spec.strip().strip('`').replace(';','')
 if ':' not in spec:spec=f'{rid}:{spec}'
 if '–' not in spec:return [spec]
 a,b=spec.split('–',1);b=b if ':' in b else a.split(':',1)[0]+':'+b;return order[order.index(a):order.index(b)+1]
def compare_grouped(actual,expected_groups):
 actual_groups=[clean(x) for x in actual.split(' … ')]
 expected=[clean(x) for x in expected_groups]
 return len(actual_groups)==len(expected) and all(a==b for a,b in zip(actual_groups,expected)),actual_groups
def locator_groups(source_line,row,order):
 plain=clean(source_line);rid=row['work_id'];locator=plain.split(',',1)[1].split('·',1)[0] if ',' in plain else ''
 groups=[]
 for chunk in [x.strip() for x in locator.split(';') if x.strip()]:
  explicit=re.findall(rf'{re.escape(rid)}:\d+(?:\.\d+)*(?:–(?:{re.escape(rid)}:)?\d+(?:\.\d+)*)?',chunk)
  tokens=explicit or re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)+(?:–\d+(?:\.\d+)*)?',chunk);keys=[]
  for token in tokens:keys.extend(expand(order,rid,token))
  if keys:groups.append(keys)
 if not groups:raise RuntimeError(f'no locator groups: {source_line}')
 return groups
def run(root=ROOT):
 p=json.loads((root/'_docs'/'theravada-reader-rewrite-progress.json').read_text());reg=json.loads((root/'_docs'/'theravada-reader-source-registry.json').read_text())['sources'];by_url={r['canonical_url'].rstrip('/'):r for r in reg};rows=[];cache={}
 for n in p.get('completed_lessons',[]):
  f=next((root/'theravada').glob(f'{n:02d}*.md'));ls=f.read_text().splitlines()
  for i,line in enumerate(ls):
   if not line.startswith('> <small>Nguồn kiểm chứng:'):continue
   u=re.search(r'href="([^"]+)"',line).group(1).rstrip('/');row=by_url[u];rid=row['work_id']
   if rid not in cache:
    api=f'https://suttacentral.net/api/bilarasuttas/{rid}/sujato?lang=en';data=json.loads(urllib.request.urlopen(api,timeout=30).read());cache[rid]=(api,data)
   api,data=cache[rid];order=data['keys_order'];root_text=data['root_text'];groups=locator_groups(line,row,order);j=i-1
   while j>=0 and not ls[j].startswith('> **Pāli**'):j-=1
   if j<0:raise RuntimeError(f'no Pāli heading {f}:{i+1}')
   k=j+1
   while k<i and not (ls[k].startswith('> *') and ls[k].endswith('*')):k+=1
   actual=ls[k][3:-1];expected_groups=[' '.join(clean(root_text[x]) for x in keys) for keys in groups];exact,actual_groups=compare_grouped(actual,expected_groups);keys=[x for group in groups for x in group]
   rows.append({'lesson':n,'source_key':row['source_key'],'work_id':rid,'segment_groups':groups,'segments':keys,'url':api,'raw_sha256':hashlib.sha256(' … '.join(' '.join(root_text[x].strip() for x in group) for group in groups).encode()).hexdigest(),'normalized_group_sha256':[hashlib.sha256(x.encode()).hexdigest() for x in expected_groups],'actual_sha256':hashlib.sha256(actual.encode()).hexdigest(),'visible_separator_count':actual.count(' … '),'group_count':len(groups),'exact_match':exact})
 report={'schema':'theravada-reader-card-exact-audit.v3','contract':'narrative-quote-v1','completed_lessons':p.get('completed_lessons',[]),'cards':len(rows),'passed':sum(r['exact_match'] for r in rows),'all_pass':all(r['exact_match'] for r in rows),'rows':rows};(root/'_docs'/'theravada-reader-card-exact-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:report[k] for k in ('completed_lessons','cards','passed','all_pass')},ensure_ascii=False));return report
if __name__=='__main__':
 r=run();raise SystemExit(0 if r['all_pass'] else 1)
