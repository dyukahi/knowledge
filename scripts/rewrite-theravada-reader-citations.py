#!/usr/bin/env python3
from __future__ import annotations
import argparse,html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES=json.loads((ROOT/'_docs'/'theravada-reader-source-registry.json').read_text())['sources'];REG={r['source_key']:r for r in SOURCES}
CODE_RE=re.compile(r'\b(DN|MN|SN|AN)\s+(\d+(?:\.\d+)?)\b')
def source_for_label(label):
 m=CODE_RE.search(label)
 if m:return REG[f"{m.group(1)} {m.group(2)}"]
 if re.search(r'\bCullavagga XI\b',label):return REG['VINAYA pli-tv-kd21']
 if re.search(r'\bCullavagga XII\b',label):return REG['VINAYA pli-tv-kd22']
 raise RuntimeError(f"unknown citation family; expand registry before migration: {label}")
def replace_reader_codes(line):
 if 'Nguồn kiểm chứng:' in line:return line
 for row in SOURCES:
  code=row.get('code','');url=re.escape(row['canonical_url']);name=row['display_title_vi'];coll=row['collection_han_viet']
  if re.fullmatch(r'(DN|MN|SN|AN) \d+(?:\.\d+)?',code):
   line=re.sub(rf'\[{re.escape(code)}(?:\s*[,—:-]\s*[^\]]+)?\]\({url}\)',f'[{name} — {coll}]({row["canonical_url"]})',line)
 def repl(m):
  key=f'{m.group(1)} {m.group(2)}';row=REG.get(key);return f'[{row["display_title_vi"]}]({row["canonical_url"]})' if row else m.group(0)
 line=CODE_RE.sub(repl,line)
 for source_key,label in [('VINAYA pli-tv-kd21','Cullavagga XI'),('VINAYA pli-tv-kd22','Cullavagga XII')]:
  row=REG[source_key]
  line=re.sub(rf'\[{re.escape(label)}\]\({re.escape(row["canonical_url"])}\)',f'[{row["display_title_vi"]} — {row["collection_han_viet"]}]({row["canonical_url"]})',line)
  line=re.sub(rf'(?<!\[)\b{re.escape(label)}\b',f'[{row["display_title_vi"]}]({row["canonical_url"]})',line)
 return line
def card_title(row):
 name=row['display_title_vi'];collection=row['collection_han_viet']
 if row['source_type']=='sutta' and not name.lower().startswith(('kinh ','lời dạy')):name='Kinh về '+name[0].lower()+name[1:]
 return f'{name} — {collection}'
def rewrite(path):
 text=path.read_text();parts=text.split('---',2);front='---'+parts[1]+'---' if len(parts)>2 else '';body=parts[2].lstrip('\n') if len(parts)>2 else text;lines=body.splitlines();out=[];i=0;cards=0
 while i<len(lines):
  line=lines[i]
  if line.startswith('> **Pāli —'):
   label=line[11:-2];row=source_for_label(label);locator=label.split(',',1)[1].strip() if ',' in label else 'đoạn theo nhãn nguồn';j=i+1;pali=[]
   while j<len(lines) and not (lines[j].startswith('> **Bản dịch') or lines[j].startswith('> **Dịch nghĩa')):
    t=lines[j].strip()
    if t.startswith('> *') and t.endswith('*'):pali.append(t[3:-1])
    j+=1
   if j>=len(lines):raise RuntimeError(f'missing translation {path}:{i+1}')
   translation=lines[j].split(':**',1)[1].strip();translation_label='Dịch Việt rút gọn' if ('…' in translation or '...' in translation) else 'Dịch Việt';source_text=re.sub(r'`','',locator).replace(row['work_id']+':','')
   out += [f'> [!quote] {card_title(row)}','> REVIEW_REQUIRED — một câu dẫn trung tính cho exact passage','>', '> **Pāli**',f'> *{" ".join(pali)}*','>',f'> **{translation_label}**',f'> {translation}','>',f'> <small>Nguồn kiểm chứng: <a href="{html.escape(row["canonical_url"])}">{html.escape(row["code"])}, {html.escape(source_text)}</a> · <i>{html.escape(row["display_title_pali"] or row["work_id"])}</i></small>'];cards+=1;i=j+1;continue
  out.append(replace_reader_codes(line));i+=1
 path.write_text((front+'\n\n' if front else '')+'\n'.join(out)+'\n');return cards
def main(argv=None):
 ap=argparse.ArgumentParser();ap.add_argument('lessons',nargs='+',type=int);a=ap.parse_args(argv);total=0
 for n in a.lessons:
  p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));c=rewrite(p);print(n,p.name,c);total+=c
 print('cards',total)

if __name__ == '__main__':
 main()
