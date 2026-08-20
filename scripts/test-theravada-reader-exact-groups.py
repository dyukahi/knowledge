#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parent/'audit-theravada-reader-cards.py';spec=importlib.util.spec_from_file_location('audit_groups',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
expected=['alpha beta','gamma delta']
cases=[('alpha beta … gamma delta',True),('alpha … gamma delta',False),('gamma delta … alpha beta',False),('alpha beta … … gamma delta',False),('alpha beta … gamma wrong',False)]
for actual,want in cases:
 got,_=m.compare_grouped(actual,expected);assert got is want,(actual,got,want)
assert m.compare_grouped('alpha beta',['alpha beta'])[0] is True
assert m.compare_grouped('alpha … beta',['alpha beta'])[0] is False
print('{"status":"pass","grouped_exact_cases":7,"adversarial_failures":5}')
