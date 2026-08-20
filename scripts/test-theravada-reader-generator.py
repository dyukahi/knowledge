#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('reader_rewrite',HERE/'rewrite-theravada-reader-citations.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
fixture='''---\ntitle: Fixture\n---\n\n# Fixture\n\n> **Pāli — MN 26, đoạn 12.1–12.3**\n> *Katamā ca, bhikkhave, ariyā pariyesanā?*\n>\n> **Dịch nghĩa làm việc:** Thế nào là cuộc tìm cầu cao quý?\n\nMN 26 được dùng ở đây để giải thích cuộc tìm cầu.\n'''
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'fixture.md';p.write_text(fixture);cards=mod.rewrite(p);out=p.read_text()
 assert cards==1
 assert '> [!quote] Kinh về ' in out
 assert '> REVIEW_REQUIRED — một câu dẫn trung tính cho exact passage' in out
 assert '> **Pāli**' in out and '> **Dịch Việt**' in out
 assert '<small>Nguồn kiểm chứng: <a href="https://suttacentral.net/mn26">' in out
 for legacy in ('Tên dễ hiểu:','Nằm ở đâu:','Đoạn này nói gì:','Nói nôm na:','Vì sao dùng ở đây:'):
  assert legacy not in out
print('{"status":"pass","contract":"narrative-quote-v1","fixtures":1}')
