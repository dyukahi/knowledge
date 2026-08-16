import fs from "node:fs"
import path from "node:path"
import { imageDimensions } from "./image-metadata.mjs"

const publicRoot = path.resolve(process.argv[2] ?? "public")

function walk(dir, suffix) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(dir, entry.name)
    return entry.isDirectory() ? walk(file, suffix) : entry.isFile() && file.endsWith(suffix) ? [file] : []
  })
}

function decodeHtml(value) {
  return value.replace(/&(?:amp|quot|apos|#39);/gi, (entity) => ({
    "&amp;": "&", "&quot;": '"', "&apos;": "'", "&#39;": "'",
  })[entity.toLowerCase()] ?? entity)
}

function contained(candidate) {
  const relative = path.relative(publicRoot, candidate)
  return relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative))
}

function unicodeExistingPath(candidate) {
  if (fs.existsSync(candidate)) return candidate
  const relative = path.relative(publicRoot, candidate)
  if (!contained(candidate)) return candidate
  let current = publicRoot
  for (const segment of relative.split(path.sep)) {
    if (!segment) continue
    if (!fs.existsSync(current) || !fs.statSync(current).isDirectory()) return candidate
    const match = fs.readdirSync(current).find((entry) => entry.normalize("NFC") === segment.normalize("NFC"))
    if (!match) return candidate
    current = path.join(current, match)
  }
  return current
}

function localImage(htmlFile, src) {
  if (!src || /^(?:data:|https?:)?\/\//i.test(src)) return null
  let pathname
  try { pathname = decodeURIComponent(decodeHtml(src).split(/[?#]/, 1)[0]).normalize("NFC") } catch { return null }
  const candidate = pathname.startsWith("/")
    ? path.join(publicRoot, pathname.replace(/^\/+/, ""))
    : path.resolve(path.dirname(htmlFile), pathname)
  return contained(candidate) ? unicodeExistingPath(candidate) : null
}

let patchedFiles = 0
let patchedImages = 0
for (const htmlFile of walk(publicRoot, ".html")) {
  let html = fs.readFileSync(htmlFile, "utf8")
  const updated = html.replace(/<img\b[^>]*>/gi, (tag) => {
    const hasWidth = /\bwidth\s*=/i.test(tag)
    const hasHeight = /\bheight\s*=/i.test(tag)
    if (hasWidth && hasHeight) return tag
    const src = tag.match(/\bsrc\s*=\s*(["'])(.*?)\1/i)?.[2]
    const image = localImage(htmlFile, src)
    if (!image || !fs.existsSync(image)) return tag
    const { width, height } = imageDimensions(image)
    patchedImages++
    const dimensions = `${hasWidth ? "" : ` width="${width}"`}${hasHeight ? "" : ` height="${height}"`}`
    return tag.replace(/\s*\/?\>$/, (ending) => `${dimensions}${ending}`)
  })
  if (updated !== html) {
    fs.writeFileSync(htmlFile, updated, "utf8")
    patchedFiles++
  }
}
console.log(`added intrinsic dimensions to ${patchedImages} images in ${patchedFiles} HTML files`)
