#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];p=ROOT/'theravada/index.md';text=p.read_text()
lessons={int(x) for x in re.findall(r'\[\[(\d{2}) - ',text)}
if lessons!=set(range(1,37)):raise SystemExit(f'gateway lesson coverage drift: missing={sorted(set(range(1,37))-lessons)} extra={sorted(lessons-set(range(1,37)))}')
modules=re.findall(r'^### ([IVX]+)\. .+? · (\d+) bài$',text,re.M)
if [int(x[1]) for x in modules]!=[4,6,6,6,6,4,4]:raise SystemExit(f'module counts drift: {modules}')
required=['không phải bách khoa toàn thư','Nếu bạn muốn hiểu Phật giáo mà không phải tắt trí để tin','Tôi Mới Bắt Đầu','Tôi Muốn Thực Hành','Tôi Muốn Đi Sâu','Thiền không thay chăm sóc y khoa hoặc tâm thần','252/252 phần nội dung','119/119 khối Pāli']
for phrase in required:
 if phrase.casefold() not in text.casefold():raise SystemExit(f'gateway missing: {phrase}')
if 'Một chương trình hoàn chỉnh, không phải tuyển tập bài tâm linh rời rạc' in text:raise SystemExit('legacy formal hero remains')
report={'schema':'theravada-gateway-audit.v1','lessons':36,'module_counts':[4,6,6,6,6,4,4],'quick_paths':3,'safety_present':True,'core_not_encyclopedia':True,'vault_voice_present':True,'all_pass':True};(ROOT/'_docs/theravada-gateway-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
