#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'theravada/index.md';text=p.read_text()
lessons={int(x) for x in re.findall(r'\[\[(\d{2}) - ',text)}
if lessons!=set(range(1,37)):raise SystemExit(f'gateway lesson coverage drift: missing={sorted(set(range(1,37))-lessons)} extra={sorted(lessons-set(range(1,37)))}')
modules=re.findall(r'^### ([IVX]+)\. .+? · (\d+) bài$',text,re.M)
if [int(x[1]) for x in modules]!=[4,6,6,6,6,4,4]:raise SystemExit(f'module counts drift: {modules}')
required=['không phải bản tóm tắt toàn bộ Kinh tạng Pāli','Muốn hiểu đạo Phật nhưng không muốn tin mù quáng','Tôi Mới Học, Nên Bắt Đầu Từ Đâu','Tôi Muốn Học Cách Thực Hành','Tôi Muốn Tìm Hiểu Nghiệp, Tái Sinh Và Nibbāna','Thiền không thay chăm sóc y khoa hoặc tâm thần','252/252 phần nội dung','119/119 khối Pāli']
for phrase in required:
 if phrase.casefold() not in text.casefold():raise SystemExit(f'gateway missing: {phrase}')
banned=['core curriculum','tension','passage','neuroscience','quantum','nde','identity','continuity','certainty','quote collection','fear porn','sci-fi','learning path']
for word in banned:
 if re.search(rf'(?i)(?<![\w]){re.escape(word)}(?![\w])',text):raise SystemExit(f'avoidable English remains: {word}')
long=[]
for number,line in enumerate(text.splitlines(),1):
 if not line.strip() or line.startswith(('#','- ','1. ','2. ','3. ','4. ','>','---')) or '→' in line or '[[' in line:continue
 for sentence in re.split(r'(?<=[.!?])\s+',line):
  words=len(re.findall(r'\w+',sentence,re.UNICODE))
  if words>55:long.append((number,words,sentence[:120]))
if long:raise SystemExit(f'gateway sentences too long: {long}')
if 'Một chương trình hoàn chỉnh, không phải tuyển tập bài tâm linh rời rạc' in text:raise SystemExit('legacy formal hero remains')
report={'schema':'theravada-gateway-audit.v2','lessons':36,'module_counts':[4,6,6,6,6,4,4],'reader_paths':3,'safety_present':True,'core_not_encyclopedia':True,'plain_vietnamese':True,'avoidable_english':0,'overlong_sentences':0,'all_pass':True};(ROOT/'_docs/theravada-gateway-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
