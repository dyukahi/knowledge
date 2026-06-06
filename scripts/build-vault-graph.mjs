import fs from "node:fs"
import path from "node:path"

const [mapPathArg, htmlOutArg, dataOutArg] = process.argv.slice(2)
const mapPath = path.resolve(mapPathArg ?? "_docs/knowledge-map.json")
const htmlOut = path.resolve(htmlOutArg ?? "vault-graph.html")
const dataOut = path.resolve(dataOutArg ?? "vault-graph-data.json")

const raw = JSON.parse(fs.readFileSync(mapPath, "utf8"))
const notes = Object.values(raw.domains ?? {})
  .flat()
  .filter((note) => note.domain !== "_docs" && !String(note.path ?? "").startsWith("_docs/"))

const byTitle = new Map()
const byPath = new Map()
for (const note of notes) {
  byPath.set(note.path, note)
  byTitle.set(note.title, note)
  const base = path.basename(note.path, ".md")
  byTitle.set(base, note)
  for (const alias of note.aliases ?? []) byTitle.set(alias, note)
}

const domainColors = {
  root: "#f59e0b",
  "crypto-finance": "#22c55e",
  esoterica: "#a855f7",
  health: "#ef4444",
  "mental-models": "#3b82f6",
  "politics-conspiracy": "#eab308",
  "science-tech": "#06b6d4",
}

const nodes = notes.map((note) => ({
  id: note.path,
  title: note.title,
  domain: note.domain,
  words: note.words ?? 0,
  backlinks: (note.backlinks ?? []).length,
  links: (note.wikilinks ?? []).length,
  aliases: note.aliases ?? [],
  url: "/" + String(note.path)
    .replace(/\\/g, "/")
    .replace(/\.md$/, "")
    .split("/")
    .map((part) => encodeURIComponent(part.replace(/\s+/g, "-")))
    .join("/"),
  color: domainColors[note.domain] ?? "#94a3b8",
}))

const links = []
const seen = new Set()
for (const note of notes) {
  for (const rawLink of note.wikilinks ?? []) {
    const targetName = String(rawLink).split("|")[0].split("#")[0].trim()
    const target = byTitle.get(targetName) ?? byPath.get(targetName) ?? byPath.get(`${targetName}.md`)
    if (!target) continue
    const key = `${note.path}→${target.path}`
    if (note.path === target.path || seen.has(key)) continue
    seen.add(key)
    links.push({ source: note.path, target: target.path })
  }
}

const graph = {
  generatedAt: new Date().toISOString(),
  stats: { nodes: nodes.length, links: links.length },
  domains: Object.fromEntries(Object.entries(domainColors).filter(([domain]) => nodes.some((n) => n.domain === domain))),
  nodes,
  links,
}

fs.mkdirSync(path.dirname(dataOut), { recursive: true })
fs.writeFileSync(dataOut, JSON.stringify(graph), "utf8")

const html = String.raw`<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Vault Graph | redpill.wiki</title>
  <meta name="description" content="Interactive graph map of redpill.wiki notes, domains, backlinks and internal connections." />
  <style>
    :root { color-scheme: dark; --bg:#0d0d10; --panel:#16161a; --text:#f4f4f5; --muted:#a1a1aa; --line:#2f3037; --accent:#84a59d; }
    * { box-sizing: border-box; }
    body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: radial-gradient(circle at top left, #1d2330, var(--bg) 42%); color:var(--text); overflow:hidden; }
    #graph { display:block; width:100vw; height:100vh; }
    .panel { position:fixed; left:16px; top:16px; width:min(420px, calc(100vw - 32px)); background: color-mix(in srgb, var(--panel) 88%, transparent); border:1px solid var(--line); border-radius:16px; padding:14px 16px; backdrop-filter: blur(10px); box-shadow: 0 16px 40px rgba(0,0,0,.35); }
    h1 { font-size:18px; margin:0 0 4px; }
    p { margin:0; color:var(--muted); line-height:1.45; font-size:13px; }
    .controls { display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }
    input, select, button { background:#0f1014; color:var(--text); border:1px solid var(--line); border-radius:10px; padding:8px 10px; font:inherit; font-size:13px; }
    input { flex:1 1 190px; min-width:0; }
    button { cursor:pointer; }
    .legend { display:flex; flex-wrap:wrap; gap:8px 12px; margin-top:10px; font-size:12px; color:var(--muted); }
    .dot { display:inline-block; width:9px; height:9px; border-radius:99px; margin-right:5px; vertical-align:middle; }
    .tip { position:fixed; right:16px; bottom:16px; max-width:min(420px, calc(100vw - 32px)); background: color-mix(in srgb, var(--panel) 90%, transparent); border:1px solid var(--line); border-radius:16px; padding:14px 16px; backdrop-filter: blur(10px); display:none; }
    .tip strong { display:block; margin-bottom:4px; }
    .tip a { color:var(--accent); text-decoration:none; }
    .small { margin-top:8px; font-size:12px; }
    @media (max-width: 700px) { .panel { top:10px; left:10px; width:calc(100vw - 20px); } .tip { left:10px; right:10px; bottom:10px; } }
  </style>
</head>
<body>
  <main id="main-content" aria-label="Vault graph visualization">
    <canvas id="graph"></canvas>
  </main>
  <section class="panel">
    <h1>Vault Graph</h1>
    <p>Bản đồ sống của redpill.wiki. Kéo để pan, scroll/pinch để zoom, click node để mở bài.</p>
    <div class="controls">
      <input id="search" placeholder="Tìm note…" />
      <select id="domain"><option value="">All domains</option></select>
      <button id="loadGraph">Load graph</button>
      <button id="reset">Reset</button>
    </div>
    <div class="legend" id="legend"></div>
    <p class="small" id="stats">Loading…</p>
  </section>
  <aside class="tip" id="tip"></aside>
<script>
const canvas = document.getElementById("graph")
const ctx = canvas.getContext("2d")
const search = document.getElementById("search")
const domainSelect = document.getElementById("domain")
const legend = document.getElementById("legend")
const tip = document.getElementById("tip")
const stats = document.getElementById("stats")
let graph, nodes, links, nodeById, scale = 1, ox = 0, oy = 0, dragging = false, last = null, hover = null
const domainOrder = ["root", "esoterica", "politics-conspiracy", "mental-models", "health", "science-tech", "crypto-finance"]
function resize(){ canvas.width = innerWidth * devicePixelRatio; canvas.height = innerHeight * devicePixelRatio; canvas.style.width = innerWidth+"px"; canvas.style.height = innerHeight+"px"; ctx.setTransform(devicePixelRatio,0,0,devicePixelRatio,0,0); draw() }
addEventListener("resize", resize)
function query(){ return search.value.trim().toLowerCase() }
function shownNodes(){ return nodes.filter(visible) }
function project(n){ return { x: n.x * scale + ox, y: n.y * scale + oy } }
function screenPos(n){
  const q = query()
  if (!q) return project(n)
  const shown = shownNodes()
  const i = Math.max(0, shown.indexOf(n))
  const cols = Math.max(1, Math.ceil(Math.sqrt(shown.length || 1)))
  return {
    x: innerWidth / 2 + (i % cols - (cols - 1) / 2) * 170,
    y: innerHeight * 0.62 + Math.floor(i / cols) * 110,
  }
}
function unproject(x,y){ return { x:(x-ox)/scale, y:(y-oy)/scale } }
function seeded(str){ let h=2166136261 >>> 0; for (let i=0;i<str.length;i++) h=Math.imul(h ^ str.charCodeAt(i), 16777619) >>> 0; return h }
function layout(){
  const W = innerWidth, H = innerHeight
  const groups = domainOrder.filter(d => nodes.some(n => n.domain===d))
  const centers = new Map(groups.map((d,i)=>[d,{x: W*(0.18+0.64*((i%4)/3)), y: H*(0.32+0.42*(Math.floor(i/4)))}]))
  for (const n of nodes){ const c=centers.get(n.domain)||{x:W/2,y:H/2}; const r=70+((seeded(n.id)%1000)/1000)*180; const a=(seeded(n.title)%6283)/1000; n.x=c.x+Math.cos(a)*r; n.y=c.y+Math.sin(a)*r; n.vx=0; n.vy=0; n.radius=Math.max(3, Math.min(12, 3 + Math.sqrt(n.backlinks+1)*1.5)) }
  // Keep the standalone graph deterministic and lightweight.
  // A force simulation can explode on dense vault graphs and leave coordinates non-finite.
  ox=0; oy=0; scale=1
}
function tick(t){
  for (const l of links){ const a=nodeById.get(l.source), b=nodeById.get(l.target); if(!a||!b) continue; const dx=b.x-a.x, dy=b.y-a.y, dist=Math.hypot(dx,dy)||1; const target=90; const f=(dist-target)*0.0009; const fx=dx*f, fy=dy*f; a.vx+=fx; a.vy+=fy; b.vx-=fx; b.vy-=fy }
  for (let i=0;i<nodes.length;i++) for (let j=i+1;j<nodes.length;j++){ const a=nodes[i], b=nodes[j]; const dx=b.x-a.x, dy=b.y-a.y, d2=dx*dx+dy*dy+0.01; if(d2>12000) continue; const f=38/d2; a.vx-=dx*f; a.vy-=dy*f; b.vx+=dx*f; b.vy+=dy*f }
  for (const n of nodes){ const c={x:innerWidth/2,y:innerHeight/2}; n.vx+=(c.x-n.x)*0.00008; n.vy+=(c.y-n.y)*0.00008; n.x+=n.vx; n.y+=n.vy; n.vx*=0.82; n.vy*=0.82 }
}
function visible(n){ const q=query(); if (domainSelect.value && n.domain!==domainSelect.value) return false; if (q && !(n.title.toLowerCase().includes(q)||n.domain.includes(q)||(n.aliases||[]).some(a=>String(a).toLowerCase().includes(q)))) return false; return true }
function draw(){ if(!nodes) return; ctx.clearRect(0,0,innerWidth,innerHeight); const q=query(); const shown=shownNodes(); ctx.lineWidth=0.55; ctx.strokeStyle="rgba(180,190,210,.13)"; ctx.beginPath(); if(!q){ for(const l of links){ const a=nodeById.get(l.source), b=nodeById.get(l.target); if(!a||!b||!visible(a)||!visible(b)) continue; const A=screenPos(a), B=screenPos(b); ctx.moveTo(A.x,A.y); ctx.lineTo(B.x,B.y) } } ctx.stroke(); for(const n of shown){ const p=screenPos(n); const r=q ? Math.max(10,n.radius*1.2) : n.radius*scale; ctx.beginPath(); ctx.fillStyle=n.color; ctx.globalAlpha = hover && hover!==n ? .45 : .92; ctx.arc(p.x,p.y,r,0,Math.PI*2); ctx.fill(); if(q || scale>1.45 || n.backlinks>12){ ctx.globalAlpha=.88; ctx.fillStyle="#f4f4f5"; ctx.font=(q ? 14 : Math.min(15, 10*scale))+"px system-ui"; ctx.fillText(n.title, p.x+r+5, p.y+5) } } ctx.globalAlpha=1; stats.textContent=(q ? shown.length+" match(es) · " : "")+graph.stats.nodes+" notes · "+graph.stats.links+" links" }
function hit(x,y){ let best=null, bd=24; for(const n of nodes){ if(!visible(n)) continue; const p=screenPos(n); const r=query()?14:n.radius*scale+5; const d=Math.hypot(p.x-x,p.y-y); if(d<Math.max(bd,r)){ best=n; bd=d } } return best }
canvas.addEventListener("pointerdown", e=>{ dragging=true; last={x:e.clientX,y:e.clientY}; canvas.setPointerCapture(e.pointerId) })
canvas.addEventListener("pointermove", e=>{ const h=hit(e.clientX,e.clientY); hover=h; canvas.style.cursor=h?"pointer":dragging?"grabbing":"grab"; if(dragging&&last){ ox+=e.clientX-last.x; oy+=e.clientY-last.y; last={x:e.clientX,y:e.clientY} } draw(); if(h){ tip.style.display="block"; tip.innerHTML="<strong>"+h.title+"</strong><span>"+h.domain+" · "+h.backlinks+" backlinks · "+h.links+" outlinks</span><br><a href=\""+h.url+"\">Mở bài →</a>" } else tip.style.display="none" })
canvas.addEventListener("pointerup", e=>{ dragging=false; if(hover && Math.hypot(e.clientX-last.x,e.clientY-last.y)<4) location.href=hover.url })
canvas.addEventListener("wheel", e=>{ e.preventDefault(); const before=unproject(e.clientX,e.clientY); scale*=Math.exp(-e.deltaY*0.001); scale=Math.max(.35,Math.min(4,scale)); const after=project(before); ox+=e.clientX-after.x; oy+=e.clientY-after.y; draw() }, {passive:false})
search.addEventListener("input", draw); domainSelect.addEventListener("change", draw); document.getElementById("reset").onclick=()=>{ if(!nodes) return loadGraph(); layout(); draw() }
stats.textContent="Click Load graph để mở bản đồ"
let loading=false
async function loadGraph(){
  if(nodes || loading) return
  loading=true
  stats.textContent="Loading graph…"
  const data=await fetch("/vault-graph-data.json").then(r=>r.json())
  graph=data; nodes=data.nodes; links=data.links; nodeById=new Map(nodes.map(n=>[n.id,n]))
  for(const d of domainOrder){ if(nodes.some(n=>n.domain===d) && ![...domainSelect.options].some(o=>o.value===d)){ const opt=document.createElement("option"); opt.value=d; opt.textContent=d; domainSelect.appendChild(opt) } }
  legend.innerHTML=Object.entries(data.domains).map(([d,c])=>"<span><i class=\"dot\" style=\"background:"+c+"\"></i>"+d+"</span>").join("")
  stats.textContent=data.stats.nodes+" notes · "+data.stats.links+" links"
  resize(); layout(); draw()
}
document.getElementById("loadGraph").onclick=loadGraph
search.addEventListener("focus", loadGraph, { once:true })
</script>
</body>
</html>`

fs.mkdirSync(path.dirname(htmlOut), { recursive: true })
fs.writeFileSync(htmlOut, html, "utf8")
console.log(`wrote ${htmlOut}`)
console.log(`wrote ${dataOut}`)
console.log(`${nodes.length} nodes, ${links.length} links`)
