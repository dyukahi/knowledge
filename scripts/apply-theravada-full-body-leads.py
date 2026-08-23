#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MARK='<!-- vault-voice-section:v1 -->'
def apply_lesson(n:int,leads:list[str]):
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));lines=p.read_text().splitlines();heads=[i for i,l in enumerate(lines) if l.startswith('## ')]
 if len(heads)!=len(leads):raise RuntimeError(f'lesson {n} heading/lead mismatch {len(heads)} != {len(leads)}')
 offset=0
 for section,(original,lead) in enumerate(zip(heads,leads),1):
  start=original+offset;end=(heads[section]+offset if section<len(heads) else len(lines));i=start+1;in_quote=False
  while i<end:
   line=lines[i]
   if line.startswith('>'):in_quote=True;i+=1;continue
   if in_quote:
    if not line.strip():i+=1;continue
    in_quote=False
   if (not line.strip() or line.startswith(('![','#','<!--','- ','```')) or line[0].isdigit() and '. ' in line[:4]):i+=1;continue
   if i>0 and lines[i-1]==MARK:break
   lines[i:i]=[MARK];offset+=1;end+=1;i+=1;lines[i]=lead+' '+lines[i];break
  else:raise RuntimeError(f'no prose paragraph lesson {n} section {section}')
 p.write_text('\n'.join(lines)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('lead_file');a=ap.parse_args();d=json.load(open(a.lead_file))['lessons']
 for key,leads in d.items():apply_lesson(int(key),leads);print(key,len(leads))
if __name__=='__main__':main()
