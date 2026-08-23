#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TECH_PREFIX=('> [!quote]','> **Pāli**','> **Dịch Việt','> <small>Nguồn kiểm chứng:')
def paragraphs(lines):
 out=[];buf=[];in_quote=False
 for line in lines:
  if line.startswith('> '):
   if buf:out.append(' '.join(buf));buf=[]
   in_quote=True;continue
  if in_quote and not line.startswith('>'):in_quote=False
  if in_quote or line.startswith(('![','<!--')):continue
  if not line.strip():
   if buf:out.append(' '.join(buf));buf=[]
  elif not line.startswith(('#','- ','1. ','2. ','3. ','4. ','5. ')):buf.append(line.strip())
 if buf:out.append(' '.join(buf))
 return out
def main():
 lessons=[];total_sections=total_paragraphs=total_words=0
 for n in range(1,37):
  p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));lines=p.read_text().splitlines();indexes=[i for i,l in enumerate(lines) if l.startswith('## ')]
  sections=[]
  for pos,start in enumerate(indexes):
   end=indexes[pos+1] if pos+1<len(indexes) else len(lines);paras=paragraphs(lines[start+1:end]);words=sum(len(re.findall(r'\w+',x,re.UNICODE)) for x in paras);concrete=sum(bool(re.search(r'\b(bạn|mình|ta|ví dụ|thử|khi |một |hãy|câu hỏi|đời sống)\b',x,re.I)) for x in paras);sections.append({'index':pos+1,'heading':lines[start][3:],'prose_paragraphs':len(paras),'prose_words':words,'concrete_paragraphs':concrete,'reviewed':False,'review_commit':None});total_sections+=1;total_paragraphs+=len(paras);total_words+=words
  lessons.append({'lesson':n,'file':p.name,'sections':sections,'section_count':len(sections),'reviewed_sections':0,'all_reviewed':False})
 report={'schema':'theravada-full-body-voice-progress.v1','baseline_commit':'f1ddbab','goal':'Paragraph-level vault voice across every H2 section; openings alone do not count.','lessons':lessons,'totals':{'lessons':36,'sections':total_sections,'prose_paragraphs':total_paragraphs,'prose_words':total_words,'reviewed_sections':0},'all_pass':False};(ROOT/'_docs/theravada-full-body-voice-progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report['totals'],ensure_ascii=False))
if __name__=='__main__':main()
