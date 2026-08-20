#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_docs'/'theravada-reference-inventory.json'
CODE_RE=re.compile(r'\b(DN|MN|SN|AN)\s+(\d+(?:\.\d+)?)\b')
rows=[];all_codes={}
for lesson in range(1,37):
 p=next((ROOT/'theravada').glob(f'{lesson:02d}*.md'));text=p.read_text();parts=text.split('---',2);front=parts[1] if len(parts)>2 else '';body=parts[2] if len(parts)>2 else text
 labels=[]
 for line in body.splitlines():
  if line.startswith('> **Pāli —'):labels.append(line[11:-2])
 mentions=[]
 for m in CODE_RE.finditer(body):
  line=body.count('\n',0,m.start())+1;snippet=body.splitlines()[line-1].strip();mentions.append({'code':f'{m.group(1)} {m.group(2)}','line':line,'snippet':snippet,'in_pali_label':snippet.startswith('> **Pāli —'),'in_source_list':snippet.startswith('- [') or 'Nguồn' in snippet})
 canonical=[];inside=False
 for line in front.splitlines():
  if line.startswith('canonical_refs:'):inside=True;continue
  if inside:
   mm=re.match(r'\s+-\s+["\']?([^"\']+)',line)
   if mm:canonical.append(mm.group(1).strip());continue
   if line and not line.startswith(' '):inside=False
 codes=sorted(set(x['code'] for x in mentions))
 for c in codes:all_codes.setdefault(c,[]).append(lesson)
 rows.append({'lesson':lesson,'file':p.name,'canonical_refs':canonical,'pali_block_count':len(labels),'pali_labels':labels,'codes':codes,'mentions':mentions,'reader_facing_bare_mentions':[x for x in mentions if not x['in_pali_label'] and not x['in_source_list']]})
out={'schema':'theravada-reference-inventory.v1','lessons':36,'unique_codes':len(all_codes),'all_codes':all_codes,'total_pali_blocks':sum(r['pali_block_count'] for r in rows),'total_mentions':sum(len(r['mentions']) for r in rows),'reader_facing_bare_mentions':sum(len(r['reader_facing_bare_mentions']) for r in rows),'rows':rows}
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:out[k] for k in ('lessons','unique_codes','total_pali_blocks','total_mentions','reader_facing_bare_mentions')},ensure_ascii=False))
