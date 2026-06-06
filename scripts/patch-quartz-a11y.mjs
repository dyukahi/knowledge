import fs from "node:fs"
import path from "node:path"

const publicRoot = process.argv[2] ? path.resolve(process.argv[2]) : path.resolve("public")

function walk(dir) {
  const out = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) out.push(...walk(full))
    else if (entry.isFile() && entry.name.endsWith(".html")) out.push(full)
  }
  return out
}

let patched = 0
for (const file of walk(publicRoot)) {
  let html = fs.readFileSync(file, "utf8")
  const before = html

  // Quartz heading anchors currently render with role="anchor"; ARIA has no such role.
  html = html.replace(/\srole="anchor"/g, "")

  // Give icon-only explorer toggle buttons accessible names.
  html = html.replace(/(<button\s+type="button"\s+class="explorer-toggle mobile-explorer[^"]*"(?![^>]*aria-label=))/g, '$1 aria-label="Mở menu điều hướng"')
  html = html.replace(/(<button\s+type="button"\s+class="title-button explorer-toggle desktop-explorer"(?![^>]*aria-label=))/g, '$1 aria-label="Thu gọn hoặc mở rộng menu điều hướng"')

  // Keep aria-expanded on interactive toggles, not passive explorer content containers.
  html = html.replace(/(<div\s+id="explorer-[^"]+"\s+class="explorer-content")\s+aria-expanded="(?:true|false)"(\s+role="group">)/g, "$1$2")

  // Lighthouse expects one main landmark. Quartz content pages use an article as the central content.
  // Convert the first content article into <main> while preserving class/name and closing tag.
  if (!/<main\b/i.test(html)) {
    let open = html.indexOf('<article class="popover-hint"')
    if (open === -1) open = html.indexOf('<article')
    if (open !== -1) {
      const openEnd = html.indexOf(">", open)
      const close = html.indexOf("</article>", openEnd)
      if (openEnd !== -1 && close !== -1) {
        html =
          html.slice(0, open) +
          html.slice(open, openEnd + 1).replace(/^<article/, '<main id="main-content"') +
          html.slice(openEnd + 1, close) +
          "</main>" +
          html.slice(close + "</article>".length)
      }
    } else if (!/<body\b/i.test(html)) {
      html = html.replace(/<\/html>\s*$/i, '<body><main id="main-content"><p>Redirecting…</p></main></body></html>')
    }
  }

  if (html !== before) {
    fs.writeFileSync(file, html, "utf8")
    patched++
  }
}

console.log(`patched accessibility in ${patched} HTML files under ${publicRoot}`)
