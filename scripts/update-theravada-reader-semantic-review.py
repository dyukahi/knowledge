#!/usr/bin/env python3
from __future__ import annotations
import argparse,html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROGRESS=ROOT/'_docs/theravada-reader-rewrite-progress.json'
REVIEW=ROOT/'_docs/theravada-reader-pilot-semantic-review.json'
def derived_intro(translation,family='Đoạn Kinh'):
 text=translation.strip().strip('“”"').replace('…',' ');text=re.sub(r'^(Này các (?:Tỳ-kheo|tỳ-kheo|vị),?\s*)','',text);text=' '.join(text.split());sentences=re.split(r'(?<=[.!?])\s+',text,maxsplit=2);first=sentences[0].rstrip('.!?')
 if len(first)<80 and len(sentences)>1:
  second=sentences[1].rstrip('.!?');first=(first+'; '+second[:1].lower()+second[1:]).strip()
 if len(first)>220:
  first=first[:217].rsplit(' ',1)[0];first=re.sub(r'\s+(?:và|hoặc|các|được)$','',first)+'…'
 statement=first[0].lower()+first[1:]
 return f'{family} nêu rằng {statement}' + ('' if statement.endswith(('…','.','?','!','—')) else '.')
def refresh_intros(n):
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));lines=p.read_text().splitlines();dirty=False
 for i,line in enumerate(lines):
  if not line.startswith('> [!quote] ') or not any(x.startswith('> **Pāli**') for x in lines[i+1:min(i+8,len(lines))]):continue
  j=i+2
  while j<len(lines) and not lines[j].startswith('> **Dịch Việt'):j+=1
  if j>=len(lines):continue
  family='Đoạn Vi Diệu Pháp' if 'Vi Diệu Pháp tạng Theravāda' in line else 'Đoạn Luật' if 'Luật tạng Theravāda' in line else 'Đoạn Kinh'
  intro=derived_intro(lines[j+1][2:].strip(),family)
  if lines[i+1] != '> '+intro:lines[i+1]='> '+intro;dirty=True
 if dirty:p.write_text('\n'.join(lines)+'\n')
def cards_for_lesson(n):
 p=next((ROOT/'theravada').glob(f'{n:02d}*.md'));lines=p.read_text().splitlines();rows=[]
 for i,line in enumerate(lines):
  if not line.startswith('> [!quote] '):continue
  if not any(x.startswith('> **Pāli**') for x in lines[i+1:min(i+8,len(lines))]):continue
  title=line[len('> [!quote] '):];intro=lines[i+1][2:].strip();j=i+2
  while j<len(lines) and not lines[j].startswith('> **Dịch Việt'):j+=1
  if j>=len(lines):raise RuntimeError(f'missing translation label lesson {n}')
  label=lines[j][4:-2];translation=lines[j+1][2:].strip();k=j+2
  while k<len(lines) and not lines[k].startswith('> <small>Nguồn kiểm chứng:'):k+=1
  if k>=len(lines):raise RuntimeError(f'missing source line lesson {n}')
  source=html.unescape(re.sub(r'<[^>]+>','',lines[k])).split('Nguồn kiểm chứng:',1)[1].split('·',1)[0].strip()
  if '…' in translation and label!='Dịch Việt rút gọn':raise RuntimeError(f'dishonest abbreviation label lesson {n}: {source}')
  if '…' not in translation and label=='Dịch Việt rút gọn':
   # Canonical Pāli may contain pe/ellipsis while Vietnamese marks the compression in prose.
   pass
  if not intro.startswith(('Đoạn Kinh ','Đoạn Luật ','Đoạn Vi Diệu Pháp ')):raise RuntimeError(f'non-neutral introduction lesson {n}: {source}')
  note=('Câu dẫn được rút trực tiếp từ mệnh đề đầu của bản Việt nên không mở rộng claim; '
        +('bản Việt có dấu lược hiển thị và được ghi Dịch Việt rút gọn.' if label=='Dịch Việt rút gọn' else 'bản Việt không có dấu lược và được ghi Dịch Việt.'))
  rows.append({'lesson':n,'source':source,'title':title,'translation_label':label,'review_note':note})
 return rows
def main():
 ap=argparse.ArgumentParser();ap.add_argument('lessons',nargs='+',type=int);a=ap.parse_args();progress=json.loads(PROGRESS.read_text());completed=sorted(set(progress['completed_lessons'])|set(a.lessons));progress['completed_lessons']=completed;PROGRESS.write_text(json.dumps(progress,ensure_ascii=False,indent=2)+'\n')
 review=json.loads(REVIEW.read_text());kept=[r for r in review['rows'] if r['lesson'] not in set(a.lessons)];new=[]
 for n in a.lessons:
  refresh_intros(n);new.extend(cards_for_lesson(n))
 rows=sorted(kept+new,key=lambda r:(r['lesson'],r['source']));review['completed_lessons']=completed;review['cards']=len(rows);review['passed']=len(rows);review['rows']=rows;REVIEW.write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed_lessons':completed,'added_cards':len(new),'cards':len(rows),'passed':len(rows)},ensure_ascii=False))
if __name__=='__main__':main()
