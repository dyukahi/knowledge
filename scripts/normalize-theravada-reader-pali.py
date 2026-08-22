#!/usr/bin/env python3
from __future__ import annotations
import json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
 audit=json.loads((ROOT/'_docs/theravada-reader-card-exact-audit.json').read_text());cache={};changed=[]
 for lesson in audit['completed_lessons']:
  rows=[r for r in audit['rows'] if r['lesson']==lesson];path=next((ROOT/'theravada').glob(f'{lesson:02d}*.md'));lines=path.read_text().splitlines();pali_lines=[]
  for i,line in enumerate(lines):
   if line.startswith('> **Pāli**'):
    j=i+1
    while j<len(lines) and not (lines[j].startswith('> *') and lines[j].endswith('*')):j+=1
    if j>=len(lines):raise RuntimeError(f'missing Pāli body lesson {lesson}')
    pali_lines.append(j)
  if len(pali_lines)!=len(rows):raise RuntimeError(f'card/audit mismatch lesson {lesson}: {len(pali_lines)} != {len(rows)}')
  dirty=False
  for line_no,row in zip(pali_lines,rows):
   if row['exact_match']:continue
   rid=row['work_id']
   if rid not in cache:
    cache[rid]=json.loads(urllib.request.urlopen(f'https://suttacentral.net/api/bilarasuttas/{rid}/sujato?lang=en',timeout=30).read())['root_text']
   root=cache[rid];expected=' … '.join(' '.join(root[key].strip() for key in group) for group in row['segment_groups']);lines[line_no]=f'> *{expected}*';dirty=True;changed.append({'lesson':lesson,'source':row['source_key'],'segments':row['segments']})
  if dirty:path.write_text('\n'.join(lines)+'\n')
 print(json.dumps({'changed_cards':len(changed),'rows':changed},ensure_ascii=False))
if __name__=='__main__':main()
