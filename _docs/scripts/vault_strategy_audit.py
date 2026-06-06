import json, re, hashlib
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "_docs"
MAP_PATH = DOCS / "knowledge-map.json"
OUT_JSON = DOCS / "vault-strategy-audit.json"
OUT_MD = DOCS / "VAULT-STRATEGY-AUDIT.md"

KEYWORD_CLUSTERS = {
    "matrix_perception": {
        "intent": "Decode reality, consciousness, epistemology, and perception models",
        "keywords_vi": ["ma trận là gì", "thoát khỏi ma trận", "ngộ đạo là gì", "vô thức tập thể"],
        "keywords_en": ["matrix meaning", "gnosis meaning", "collective unconscious", "reality perception model"],
        "signals": ["matrix", "ma trận", "gnosis", "consciousness", "perception", "vô thức", "nhận thức"],
    },
    "predictive_programming": {
        "intent": "Understand media spectacle, symbolism, and synchronized mass attention",
        "keywords_vi": ["predictive programming là gì", "nghi lễ đại chúng", "biểu tượng Hollywood"],
        "keywords_en": ["predictive programming", "spectacle ritual", "Hollywood occult symbolism"],
        "signals": ["predictive", "spectacle", "hollywood", "ritual", "nghi lễ", "world cup", "super bowl", "inception"],
    },
    "health_sovereignty": {
        "intent": "Natural health, terrain theory, metabolic protocols, and medical skepticism",
        "keywords_vi": ["y tế tự nhiên", "terrain theory", "ung thư metabolic protocol", "fasting chữa lành"],
        "keywords_en": ["health sovereignty", "terrain theory", "metabolic cancer protocol", "natural healing protocol"],
        "signals": ["health", "y tế", "terrain", "ung thư", "cancer", "fasting", "metabolic", "tuyến tùng", "thuốc"],
    },
    "financial_sovereignty": {
        "intent": "Money psychology, fiat critique, Bitcoin privacy, CBDC/control rails",
        "keywords_vi": ["tiền pháp định là gì", "bitcoin privacy", "cbdc là gì", "giữ tiền hơn kiếm tiền"],
        "keywords_en": ["fiat currency", "Bitcoin privacy", "CBDC programmable money", "financial sovereignty"],
        "signals": ["bitcoin", "privacy", "cbdc", "fiat", "tiền", "money", "finance", "risk", "market"],
    },
    "science_revisionism": {
        "intent": "Alternative science, suppressed tech, cosmology, aether, and institution critique",
        "keywords_vi": ["khoa học xét lại", "Nikola Tesla", "năng lượng aether", "địa tâm"],
        "keywords_en": ["science revisionism", "Nikola Tesla suppressed technology", "aether energy", "geocentrism"],
        "signals": ["science", "khoa học", "tesla", "aether", "địa tâm", "antikythera", "russell", "nuclear", "hạt nhân"],
    },
    "current_events_lab": {
        "intent": "Read current events as laboratories of narrative, policy, symbol, and compliance",
        "keywords_vi": ["phòng thí nghiệm sự kiện", "phân tích sự kiện", "UAP disclosure", "Digital ID"],
        "keywords_en": ["current events lab", "controlled revelation", "digital ID normalization", "climate anxiety control"],
        "signals": ["2026", "maga", "uap", "digital id", "climate anxiety", "world cup", "elisel", "normalization", "disclosure"],
    },
    "redpill_onboarding": {
        "intent": "Brand, source discipline, glossary, methodology, and how to read the vault",
        "keywords_vi": ["redpill wiki", "cách đọc red pill wiki", "từ điển red pill", "kỷ luật nguồn"],
        "keywords_en": ["redpill wiki", "red pill wiki Vietnamese", "how to read redpill wiki", "source discipline"],
        "signals": ["red pill", "source discipline", "glossary", "cách đọc", "index", "moc", "methodology"],
    },
}

HIGH_RISK_TERMS = [
    "ung thư", "cancer", "fasting", "metabolic", "thuốc", "y tế", "vaccine", "pharma", "terrain", "vi sinh",
    "elite", "agenda", "2030", "mind control", "kiểm soát", "rockefeller", "flat earth", "trái đất phẳng",
    "antarctica", "nazi", "mindgeek", "porn", "khế ước", "secret covenant", "hạt nhân", "nuclear", "radiation",
    "directed energy", "vũ khí", "uap", "disclosure", "digital id", "cbdc", "climate anxiety"
]
SOURCE_SAFE_TERMS = ["source discipline", "kỷ luật nguồn", "evidence discipline", "how to read", "cách đọc", "fact /", "pattern /", "symbol /", "speculative", "giả thuyết", "không phải", "not medical", "medical advice", "vault position"]
UTILITY_PATTERNS = ["index.md", "README.md", "MOC -", "Glossary", "Cách Đọc", "Source Discipline", "Current Events Lab", "llms.txt"]


def read_text(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def rel(path): return str(path).replace("\\", "/")

def classify_priority(score):
    if score >= 80: return "P0"
    if score >= 55: return "P1"
    if score >= 35: return "P2"
    return "P3"

def titleish(note): return note.get("title") or Path(note["path"]).stem

def body_for(note):
    p = ROOT / note["path"]
    return read_text(p) if p.exists() and p.suffix.lower() == ".md" else ""

def has_any(hay, needles):
    h=hay.lower()
    return any(n.lower() in h for n in needles)

with MAP_PATH.open(encoding="utf-8-sig") as f:
    data=json.load(f)
notes=[]
for note in data["notes"].values():
    if note["path"].startswith("_docs/"):
        continue
    note=note.copy()
    note["degree"] = len(note.get("outlinks",[])) + len(note.get("backlinks",[]))
    note["is_utility"] = any(pat.lower() in note["path"].lower() for pat in UTILITY_PATTERNS) or note["domain"] in ["root"] and note["words"] < 900 and ("MOC" in titleish(note) or "Gateway" in titleish(note))
    text=(note["path"]+" "+titleish(note)+" "+" ".join(note.get("tags",[]))+" "+note.get("summary","")).lower()
    note["cluster_hits"]=[]
    for cname,c in KEYWORD_CLUSTERS.items():
        hits=sum(1 for s in c["signals"] if s.lower() in text)
        if hits: note["cluster_hits"].append((cname,hits))
    notes.append(note)

# Read bodies only for risk/source/current scoring, not for full manual article audit.
for n in notes:
    b=body_for(n)
    full=((n["path"]+" "+titleish(n)+" "+" ".join(n.get("tags",[]))+" "+n.get("summary","")+" "+b[:20000])).lower()
    n["risk_hits"]=[t for t in HIGH_RISK_TERMS if t in full]
    n["source_safe_hits"]=[t for t in SOURCE_SAFE_TERMS if t in full]
    n["has_sources_field"] = bool(re.search(r"(?m)^sources\s*:", b[:3000], re.I))
    n["has_aliases"] = bool(n.get("aliases"))
    n["headings_count"] = len(n.get("headings",[]))

# Queues
flagship=[]
for n in notes:
    if n["is_utility"]: continue
    score=n["degree"]*1.4 + min(n["words"]/40,50) + (15 if n["backlinks"] and len(n["backlinks"])>20 else 0)
    if any(c in [x[0] for x in n["cluster_hits"]] for c in ["matrix_perception","health_sovereignty","financial_sovereignty","science_revisionism","predictive_programming"]): score += 10
    if score>=55:
        flagship.append({"path":n["path"],"title":titleish(n),"priority":classify_priority(score),"score":round(score,1),"reason":f"High graph centrality (degree {n['degree']}, backlinks {len(n.get('backlinks',[]))}) plus {n['words']} words; strong candidate to become/serve as a public landing article.","next_action":"Tighten intro/meta, add Source/Vault Position if controversial, ensure 5-8 strategic internal links, then consider featuring in index/MOC."})
flagship=sorted(flagship,key=lambda x:(x["priority"],-x["score"]))[:35]

expand=[]
thin_paths={}
thin_doc=DOCS/"THIN-PAGE-CLASSIFICATION.md"
if thin_doc.exists():
    for line in read_text(thin_doc).splitlines():
        m=re.match(r"\|\s*(\d+)\s*\|\s*(expand|keep|utility)\s*\|\s*`([^`]+)`\s*\|\s*(.*?)\s*\|", line)
        if m: thin_paths[m.group(3)]={"words":int(m.group(1)),"class":m.group(2),"rationale":m.group(4)}
for n in notes:
    score=0
    reasons=[]
    if n["path"] in thin_paths and thin_paths[n["path"]]["class"]=="expand": score+=55; reasons.append("already classified as expand in thin-page audit")
    if n["words"]<900 and not n["is_utility"] and n["degree"]>=10: score+=25; reasons.append(f"short but connected ({n['words']} words, degree {n['degree']})")
    if n["cluster_hits"] and n["words"]<1300 and not n["is_utility"]: score+=20; reasons.append("matches an SEO/search-intent cluster")
    if n["risk_hits"] and not n["source_safe_hits"]: score+=15; reasons.append("controversial topic lacks obvious source-discipline framing")
    if score>=40:
        expand.append({"path":n["path"],"title":titleish(n),"priority":classify_priority(score),"score":score,"reason":"; ".join(reasons),"next_action":"Expand only with a defined angle: add Vault Position/Evidence Discipline, glossary terms if needed, and 3-5 contextual internal links. Avoid padding for word count."})
expand=sorted(expand,key=lambda x:(x["priority"],-x["score"],x["path"]))[:45]

utility=[]
for n in notes:
    if n["is_utility"] or (n["path"] in thin_paths and thin_paths[n["path"]]["class"] in ["utility","keep"]):
        if len(utility)<45:
            cls=thin_paths.get(n["path"],{}).get("class", "utility" if n["is_utility"] else "keep")
            utility.append({"path":n["path"],"title":titleish(n),"classification":cls,"reason":"Navigation/reference/short evergreen page where usefulness beats length." if cls=="utility" else "Short evergreen note acceptable until it becomes a priority page.","next_action":"Keep short; improve snippets/internal links opportunistically, do not force artificial expansion."})

risk=[]
for n in notes:
    if not n["risk_hits"]: continue
    severity = len(set(n["risk_hits"])) + (3 if n["domain"] in ["health","politics-conspiracy"] else 0) + (2 if n["words"]<1000 else 0)
    safe = bool(n["source_safe_hits"] or n["has_sources_field"])
    risk.append({"path":n["path"],"title":titleish(n),"priority":"P0" if severity>=8 and not safe else ("P1" if severity>=5 else "P2"),"status":"already-safer" if safe else "needs-source-discipline","risk_signals":sorted(set(n["risk_hits"]))[:8],"source_safety_signals":sorted(set(n["source_safe_hits"]))[:8],"reason":"High-stakes health/politics/science/control topic; reader needs claim-layering and evidence boundaries." if not safe else "Controversial/high-stakes topic but already shows source/evidence or caveat language; still worth spot-checking before flagship promotion.","next_action":"Add/strengthen Vault Position or Evidence Discipline and separate fact/pattern/symbol/speculation." if not safe else "Preserve framing; verify strongest claims before further promotion."})
risk=sorted(risk,key=lambda x:(x["priority"], x["status"], x["path"]))[:70]

seo=[]
for n in notes:
    if n["is_utility"] and "MOC" not in titleish(n) and n["path"] not in ["index.md","Cách Đọc Red Pill Wiki.md","Glossary - Từ Điển Red Pill Wiki.md","Source Discipline - Kỷ Luật Nguồn Và Bằng Chứng.md"]: continue
    for cname,hits in sorted(n["cluster_hits"], key=lambda x:-x[1])[:2]:
        c=KEYWORD_CLUSTERS[cname]
        score=hits*20 + min(n["degree"],50) + (10 if n["words"]>1000 else 0)
        if score>=25:
            seo.append({"path":n["path"],"title":titleish(n),"cluster":cname,"priority":classify_priority(score),"score":score,"search_intent":c["intent"],"keyword_hypotheses_vi":c["keywords_vi"][:3],"keyword_hypotheses_en":c["keywords_en"][:3],"reason":f"Matches {hits} cluster signals and has degree {n['degree']}; likely search landing/support page.","next_action":"Add answer-first definition, tighten description/aliases, and link from relevant MOC/cluster page."})
seo=sorted(seo,key=lambda x:(x["priority"],-x["score"],x["path"]))[:60]

cel=[]
for n in notes:
    text=(n["path"]+" "+titleish(n)+" "+" ".join(n.get("tags",[]))+" "+n.get("summary","")).lower()
    signals=[s for s in KEYWORD_CLUSTERS["current_events_lab"]["signals"] if s in text]
    if signals or re.search(r"\b20(2[4-9]|3\d)\b", text):
        cel.append({"path":n["path"],"title":titleish(n),"priority":"P1" if signals else "P2","signals":signals[:6],"reason":"Event/policy/media-specific note suitable for the Current Events Lab format.","next_action":"Convert/promote as lab case: timestamp facts, define pattern hypothesis, mark symbol/speculation layers, and link to Source Discipline."})
cel=sorted(cel,key=lambda x:(x["priority"],x["path"]))[:35]

# Coverage stats
by_domain={}
for n in notes:
    d=n["domain"]; by_domain.setdefault(d,{"notes":0,"words":0,"utility":0,"risk":0})
    by_domain[d]["notes"]+=1; by_domain[d]["words"]+=n["words"]
    by_domain[d]["utility"]+=int(n["is_utility"])
    by_domain[d]["risk"]+=int(bool(n["risk_hits"]))
for d in by_domain.values(): d["avg_words"]=round(d["words"]/d["notes"])

report={
    "generated_at":"2026-06-06T07:43:00+07:00",
    "source_map":"_docs/knowledge-map.json",
    "map_stats":data.get("stats",{}),
    "coverage":{"audited_public_notes":len(notes),"domains":by_domain,"queue_counts":{"flagship_candidates":len(flagship),"expand_candidates":len(expand),"utility_keep_short_pages":len(utility),"high_risk_notes":len(risk),"seo_potential_candidates":len(seo),"current_events_lab_candidates":len(cel)}},
    "queues":{"flagship_candidates":flagship,"expand_candidates":expand,"utility_keep_short_pages":utility,"high_risk_notes":risk,"seo_potential_candidates":seo,"current_events_lab_candidates":cel},
    "method":"Map-first audit using graph degree/backlinks/outlinks, word count, prior SEO/thin-page docs, keyword cluster signals, and targeted body scans for source-discipline/risk terms. This is editorial guidance, not a claim-validity review."
}
OUT_JSON.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")

def table(rows, cols, max_rows=None):
    rows=rows[:max_rows] if max_rows else rows
    out=["| " + " | ".join(h for h,_ in cols) + " |", "|"+"|".join("---" for _ in cols)+"|"]
    for r in rows:
        vals=[]
        for _,key in cols:
            v=r
            for part in key.split('.'):
                v=v.get(part,{}) if isinstance(v,dict) else ""
            if isinstance(v,list): v=", ".join(map(str,v))
            vals.append(str(v).replace("\n"," ").replace("|","/"))
        out.append("| "+" | ".join(vals)+" |")
    return "\n".join(out)

md=[]
md.append("# Vault Strategy Audit — redpill.wiki\n")
md.append("Generated: 2026-06-06 GMT+7  \nScope: whole-vault strategy pass based on `_docs/knowledge-map.json`, existing SEO/thin-page docs, root index/MOCs, and targeted article metadata/body scans.\n")
md.append("## Executive read\n")
md.append(f"- Public notes audited: **{len(notes)}**. Map snapshot says **{data['stats'].get('notes')} notes**, **{data['stats'].get('wikilinkEdges')} resolved internal edges**, **{data['stats'].get('brokenLinks')} broken links**, **{data['stats'].get('orphans')} orphans**.\n- The vault already has strong hub gravity around `Ma Trận`, `Elite`, `Khoa Học Xét Lại`, `Gnosis`, Health Sovereignty, and MOCs. Strategy should now split pages into **flagships**, **expand only with angle**, **utility keep-short**, and **high-risk/source-discipline** lanes.\n- Biggest strategic opportunity: turn hub notes + MOCs into bilingual answer-first landing pages without flattening the vault voice. Biggest risk: promoting health/politics/science-revision notes before claim layers are explicit.\n")
md.append("## Domain coverage\n")
md.append(table([{"domain":k,**v} for k,v in sorted(by_domain.items())],[('Domain','domain'),('Notes','notes'),('Avg words','avg_words'),('Utility','utility'),('Risk-signal notes','risk')]))
md.append("\n## Queue 1 — Flagship candidates\n")
md.append("These are the pages with enough graph gravity and topical breadth to act as public pillars, series anchors, or landing pages.\n")
md.append(table(flagship,[('Priority','priority'),('Path','path'),('Score','score'),('Reason','reason'),('Next action','next_action')]))
md.append("\n## Queue 2 — Expand candidates\n")
md.append("Expand these only when there is a clear editorial/search angle. Do not pad for word count.\n")
md.append(table(expand,[('Priority','priority'),('Path','path'),('Score','score'),('Reason','reason'),('Next action','next_action')]))
md.append("\n## Queue 3 — Utility / keep-short pages\n")
md.append("Short is fine here. Their job is routing, orientation, or atomic evergreen support.\n")
md.append(table(utility,[('Class','classification'),('Path','path'),('Reason','reason'),('Next action','next_action')], max_rows=55))
md.append("\n## Queue 4 — High-risk notes: Source Discipline status\n")
md.append("`needs-source-discipline` means the topic is high-stakes and the scan did not find obvious evidence/caveat language. `already-safer` means there are caveat/source-position signals, not that every claim is validated.\n")
md.append(table(risk,[('Priority','priority'),('Status','status'),('Path','path'),('Risk signals','risk_signals'),('Reason','reason'),('Next action','next_action')], max_rows=80))
md.append("\n## Queue 5 — SEO potential candidates\n")
md.append("Keyword hypotheses are editorial hypotheses until GSC/SERP data exists.\n")
md.append(table(seo,[('Priority','priority'),('Cluster','cluster'),('Path','path'),('Search intent','search_intent'),('VI hypotheses','keyword_hypotheses_vi'),('EN hypotheses','keyword_hypotheses_en'),('Next action','next_action')], max_rows=70))
md.append("\n## Queue 6 — Current Events Lab candidates\n")
md.append("These should use a lab format: timestamped facts, pattern hypothesis, symbol layer, speculation boundary, and links back to Source Discipline.\n")
md.append(table(cel,[('Priority','priority'),('Path','path'),('Signals','signals'),('Reason','reason'),('Next action','next_action')], max_rows=40))
md.append("\n## Recommended next 90-day editorial sequence\n")
md.append("1. **Source Discipline pass first:** fix P0/P1 `needs-source-discipline` items before pushing them as flagships.\n2. **Flagship polish wave:** choose 8-12 P0/P1 flagships, add answer-first intros, clearer aliases/descriptions, and MOC/index paths.\n3. **SEO bridge wave:** add short `Từ Khóa Cần Hiểu` / answer-first sections to pages already matching keyword clusters.\n4. **Current Events Lab template:** standardize one format and backfill the event/policy/symbol notes so they age well.\n5. **Utility hygiene:** keep MOCs short but strengthen their reading paths and snippets.\n")
md.append("\n## Method notes / limitations\n")
md.append("- This audit is map-first and metadata-driven, with targeted scans for risk/source signals. It is not a full factual verification of every claim.\n- Existing broken-link status was taken from the current generated map and later validated after writing reports.\n- JSON companion: `_docs/vault-strategy-audit.json`.\n")
OUT_MD.write_text("\n".join(md),encoding="utf-8")
print(f"wrote {OUT_MD}")
print(f"wrote {OUT_JSON}")
print(json.dumps(report['coverage'],ensure_ascii=False,indent=2))
