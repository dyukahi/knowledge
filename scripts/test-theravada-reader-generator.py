#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reader_rewrite',HERE/'rewrite-theravada-reader-citations.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
def run_fixture(text,repeat=False):
 with tempfile.TemporaryDirectory() as td:
  p=Path(td)/'fixture.md';p.write_text(text);cards=mod.rewrite(p);first=p.read_text()
  if repeat:mod.rewrite(p);assert p.read_text()==first
  return cards,first
nikaya='''---\ntitle: Fixture\n---\n# Fixture\n> **Pāli — MN 26, đoạn 12.1–12.3**\n> *Katamā ca, bhikkhave, ariyā pariyesanā?*\n> **Dịch nghĩa làm việc:** Thế nào là cuộc tìm cầu cao quý?\nMN 26 được dùng ở đây.\n'''
cards,out=run_fixture(nikaya);assert cards==1 and '> [!quote] Kinh về ' in out and 'https://suttacentral.net/mn26' in out
vinaya='''---\ntitle: Vinaya Fixture\n---\n# Fixture\n> **Pāli — Cullavagga XI, các đoạn pli-tv-kd21:1.11.4–pli-tv-kd21:1.11.7**\n> *Handa mayaṁ āvuso dhammañca vinayañca saṅgāyissāma.*\n> **Dịch nghĩa làm việc:** Này các hiền giả, chúng ta hãy cùng tụng đọc Pháp và Luật.\nCullavagga XI được dùng ở đây.\n'''
cards,out=run_fixture(vinaya,repeat=True);assert cards==1 and '> [!quote] Chương Luật về kỳ kết tập đầu tiên — Luật tạng Theravāda' in out and 'https://suttacentral.net/pli-tv-kd21' in out and 'pli-tv-kd21:' not in out.split('Nguồn kiểm chứng:',1)[1]
assert mod.replace_reader_codes('Cullavagga XI và Cullavagga XII').count('suttacentral.net')==2
linked='[Cullavagga XI](https://suttacentral.net/pli-tv-kd21)'
fixed=mod.replace_reader_codes(linked);assert fixed.count('](')==1 and '[[Chương' not in fixed
assert 'tranh chấp Vesālī' not in mod.replace_reader_codes('Cullavagga XI')
try:mod.source_for_label('Unknown Canon 1')
except RuntimeError as e:assert 'unknown citation family' in str(e)
else:raise AssertionError('unknown family must fail')
for output in (out,):
 for legacy in ('Tên dễ hiểu:','Nằm ở đâu:','Đoạn này nói gì:','Nói nôm na:','Vì sao dùng ở đây:'):assert legacy not in output
print('{"status":"pass","contract":"narrative-quote-v1","fixtures":2,"families":["nikaya","vinaya"]}')
