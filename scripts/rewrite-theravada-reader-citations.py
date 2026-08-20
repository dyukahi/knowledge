#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REG={r['code']:r for r in json.loads((ROOT/'_docs'/'theravada-reader-source-registry.json').read_text())['sources']}
CODE_RE=re.compile(r'\b(DN|MN|SN|AN)\s+(\d+(?:\.\d+)?)\b')
def first_sentence(lines,start):
 for line in lines[start:]:
  t=line.strip()
  if not t or t.startswith('>') or t.startswith('![') or t.startswith('<!--'):continue
  t=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',t);parts=re.split(r'(?<=[.!?])\s+',t);return parts[0][:420]
 return 'Đoạn Kinh này là nền nguồn trực tiếp cho phần giải thích ngay sau đó.'
def reader_name(code):return REG[code]['discourse_plain_vietnamese_title']
def replace_reader_codes(line):
 if line.startswith('> **Mã kiểm chứng:**'):return line
 # Replace existing markdown links whose label begins with a code.
 for code,row in REG.items():
  url=re.escape(row['url']);line=re.sub(rf'\[{re.escape(code)}(?:\s*[,—:-]\s*[^\]]+)?\]\({url}\)',f'[{row["discourse_plain_vietnamese_title"]} — {row["collection_han_viet"]}]({row["url"]})',line)
 def repl(m):
  code=f'{m.group(1)} {m.group(2)}';row=REG.get(code)
  return f'[{row["discourse_plain_vietnamese_title"]}]({row["url"]})' if row else m.group(0)
 return CODE_RE.sub(repl,line)
def rewrite(path):
 text=path.read_text();parts=text.split('---',2);front='---'+parts[1]+'---' if len(parts)>2 else '';body=parts[2].lstrip('\n') if len(parts)>2 else text;lines=body.splitlines();out=[];i=0;cards=0
 while i<len(lines):
  line=lines[i]
  if line.startswith('> **Pāli —'):
   m=CODE_RE.search(line)
   if not m:raise RuntimeError(f'unparsed Pāli label {path}:{i+1}: {line}')
   code=f'{m.group(1)} {m.group(2)}';row=REG[code];label=line[11:-2];segment=label.split(',',1)[1].strip() if ',' in label else 'segment theo nhãn nguồn';j=i+1;pali=[]
   while j<len(lines) and not (lines[j].startswith('> **Bản dịch') or lines[j].startswith('> **Dịch nghĩa')):
    t=lines[j].strip()
    if t.startswith('> *') and t.endswith('*'):pali.append(t[3:-1])
    j+=1
   if j>=len(lines):raise RuntimeError(f'missing translation {path}:{i+1}')
   translation=lines[j].split(':**',1)[1].strip().strip('“”')
   pali_title=f'*{row["discourse_pali_title"]}*' if row.get('discourse_pali_title') else 'tên Pāli chưa khóa'
   translation_label='Dịch rút gọn có đánh dấu' if ('…' in translation or '...' in translation) else 'Dịch sát nghĩa'
   card=[
    '> [!quote] Nguồn Kinh dễ hiểu',
    f'> **Tên dễ hiểu:** {row["discourse_plain_vietnamese_title"]}',
   ]
   if row.get('discourse_han_viet_title'):
    card.append(f'> **Tên truyền thống/Hán-Việt:** {row["discourse_han_viet_title"]}')
   card += [
    f'> **Nằm ở đâu:** {pali_title}, bài {row["number"]} của {row["collection_han_viet"]} (*{row["collection_pali"]}*)',
    '> **Đoạn này nói gì:** REVIEW_REQUIRED — mô tả literal nội dung exact segment',
    f'> **Mã kiểm chứng:** [`{code}`, {segment}]({row["url"]})',
    f'> **Pāli gốc:** *{" ".join(pali)}*',
    f'> **{translation_label}:** {translation}',
    '> **Nói nôm na:** REVIEW_REQUIRED — một takeaway bình dân',
    '> **Vì sao dùng ở đây:** REVIEW_REQUIRED — claim cụ thể được nguồn hỗ trợ',
   ]
   out += card;cards+=1;i=j+1;continue
  out.append(replace_reader_codes(line));i+=1
 new=(front+'\n\n' if front else '')+'\n'.join(out)+'\n';path.write_text(new);return cards
ap=argparse.ArgumentParser();ap.add_argument('lessons',nargs='+',type=int);a=ap.parse_args();total=0
for n in a.lessons:
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));c=rewrite(p);print(n,p.name,c);total+=c
print('cards',total)
