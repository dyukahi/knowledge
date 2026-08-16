import fs from "node:fs"
import path from "node:path"
import { imageDimensions } from "./image-metadata.mjs"

const root = path.resolve(process.argv[2] ?? "public")
const siteOrigin = "https://redpill.wiki"
const stableSiteDescription =
  "Red Pill Wiki là kho tri thức độc lập về tư duy phản biện, chủ quyền cá nhân, lịch sử, khoa học, tài chính và ý thức."
const errors = []

function walk(dir, predicate) {
  if (!fs.existsSync(dir)) return []
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(dir, entry.name)
    return entry.isDirectory() ? walk(file, predicate) : entry.isFile() && predicate(file) ? [file] : []
  })
}

function decodeHtml(value = "") {
  return value.replace(/&(?:amp|lt|gt|quot|apos|#39|#x[0-9a-f]+|#[0-9]+);/gi, (entity) => {
    const lower = entity.toLowerCase()
    const named = { "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&apos;": "'", "&#39;": "'" }
    if (named[lower]) return named[lower]
    const hex = lower.match(/^&#x([0-9a-f]+);$/)
    const decimal = lower.match(/^&#([0-9]+);$/)
    const codePoint = hex ? Number.parseInt(hex[1], 16) : decimal ? Number.parseInt(decimal[1], 10) : NaN
    try { return Number.isFinite(codePoint) ? String.fromCodePoint(codePoint) : entity } catch { return entity }
  })
}

function normalizeRoute(value) {
  try {
    const decoded = decodeURIComponent(value).normalize("NFC").replace(/\/{2,}/g, "/")
    const withoutIndex = decoded.replace(/\/index(?:\.html)?$/i, "/").replace(/\.html$/i, "")
    return withoutIndex !== "/" ? withoutIndex.replace(/\/$/, "") : "/"
  } catch {
    return null
  }
}

function attr(tag, name) {
  const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  return decodeHtml(tag.match(new RegExp(`(?:^|\\s)${escaped}\\s*=\\s*(["'])(.*?)\\1`, "i"))?.[2] ?? "") || undefined
}

function meta(html, key) {
  const lowerKey = key.toLowerCase()
  const tag = (html.match(/<meta\b[^>]*>/gi) ?? []).find((candidate) =>
    [attr(candidate, "name"), attr(candidate, "property")].some((value) => value?.toLowerCase() === lowerKey),
  )
  return tag ? attr(tag, "content") : undefined
}

function metaHttpEquiv(html, key) {
  const lowerKey = key.toLowerCase()
  const tag = (html.match(/<meta\b[^>]*>/gi) ?? []).find(
    (candidate) => attr(candidate, "http-equiv")?.toLowerCase() === lowerKey,
  )
  return tag ? attr(tag, "content") : undefined
}

function pageUrl(route) {
  return new URL(route === "/" ? "/" : route, siteOrigin)
}

function refreshTarget(content, base) {
  if (!content) return undefined
  const match = content.match(/^\s*\d+(?:\.\d+)?\s*;\s*url\s*=\s*(.*?)\s*$/i)
  if (!match) return null
  const value = match[1].replace(/^(["'])([\s\S]*)\1$/, "$2").trim()
  if (!value) return null
  try { return new URL(value, base) } catch { return null }
}

function contained(candidate) {
  const relative = path.relative(root, candidate)
  return relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative))
}

function unicodeExistingPath(candidate) {
  if (fs.existsSync(candidate)) return candidate
  if (!contained(candidate)) return candidate
  const relative = path.relative(root, candidate)
  let current = root
  for (const segment of relative.split(path.sep)) {
    if (!segment) continue
    if (!fs.existsSync(current) || !fs.statSync(current).isDirectory()) return candidate
    const match = fs.readdirSync(current).find((entry) => entry.normalize("NFC") === segment.normalize("NFC"))
    if (!match) return candidate
    current = path.join(current, match)
  }
  return current
}

function localAsset(htmlFile, src) {
  if (!src || /^(?:data:|https?:)?\/\//i.test(src)) return null
  let pathname
  try { pathname = decodeURIComponent(src.split(/[?#]/, 1)[0]).normalize("NFC") } catch { return { invalid: true } }
  const candidate = pathname.startsWith("/")
    ? path.join(root, pathname.replace(/^\/+/, ""))
    : path.resolve(path.dirname(htmlFile), pathname)
  if (!contained(candidate)) return { invalid: true }
  return { path: unicodeExistingPath(candidate) }
}

function emittedRoute(file) {
  const relative = path.relative(root, file).split(path.sep).join("/")
  return normalizeRoute(relative === "index.html" ? "/" : `/${relative}`)
}

if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) {
  console.error(`built-site validation failed: public root does not exist: ${root}`)
  process.exit(1)
}

const htmlFiles = walk(root, (file) => file.endsWith(".html"))
const routes = new Set(htmlFiles.map(emittedRoute).filter(Boolean))
const pages = htmlFiles.map((file) => ({ file, html: fs.readFileSync(file, "utf8"), route: emittedRoute(file) }))
const descriptions = new Map()
const noindexUtilityRoutes = new Set()
let indexableCanonicalPageCount = 0
let noindexUtilityPageCount = 0
let aliasRedirectCount = 0

for (const { file, html, route } of pages) {
  const label = path.relative(root, file)
  const is404 = path.basename(file) === "404.html"
  const currentPageUrl = pageUrl(route)
  const refreshContent = metaHttpEquiv(html, "refresh")
  const redirectTarget = refreshContent === undefined ? undefined : refreshTarget(refreshContent, currentPageUrl)
  const title = decodeHtml(html.match(/<title>([\s\S]*?)<\/title>/i)?.[1] ?? "").trim()
  const description = meta(html, "description") ?? ""
  const robots = (meta(html, "robots") ?? "").toLowerCase().split(/[\s,]+/).filter(Boolean)
  const isNoindex = robots.includes("noindex") || robots.includes("none")
  const isTagRoute = route === "/tags" || route?.startsWith("/tags/")
  const canonicalHref = (html.match(/<link\b[^>]*rel=["'][^"']*canonical[^"']*["'][^>]*>/i)
    ?? html.match(/<link\b[^>]*href=["'][^"']+["'][^>]*rel=["'][^"']*canonical[^"']*["'][^>]*>/i))?.[0]
  const canonicalValue = canonicalHref ? attr(canonicalHref, "href") : undefined
  let canonical
  if (canonicalValue) {
    try { canonical = new URL(canonicalValue, currentPageUrl) } catch { errors.push(`${label}: malformed canonical ${canonicalValue}`) }
  }

  if (refreshContent !== undefined) {
    aliasRedirectCount += 1
    if (!redirectTarget) errors.push(`${label}: malformed meta refresh ${refreshContent}`)
    else if (redirectTarget.origin !== siteOrigin) errors.push(`${label}: redirect has wrong origin ${redirectTarget.href}`)
    else {
      const destinationRoute = normalizeRoute(redirectTarget.pathname)
      if (!destinationRoute) errors.push(`${label}: malformed redirect route ${redirectTarget.href}`)
      else if (!routes.has(destinationRoute)) errors.push(`${label}: missing redirect destination ${redirectTarget.href} -> ${destinationRoute}`)
      if (canonical && canonical.href !== redirectTarget.href) {
        errors.push(`${label}: canonical and redirect destinations differ (${canonical.href} != ${redirectTarget.href})`)
      }
    }
    continue
  }

  if (!is404) {
    if (isTagRoute && !isNoindex) errors.push(`${label}: tag utility page must be noindex`)
    if (!isTagRoute && isNoindex) errors.push(`${label}: normal canonical page must remain indexable`)
    const isNoindexUtility = isTagRoute && isNoindex
    if (isNoindexUtility) {
      noindexUtilityPageCount += 1
      noindexUtilityRoutes.add(route)
    } else {
      indexableCanonicalPageCount += 1
    }
    if (!title) errors.push(`${label}: missing title`)
    else if (!isNoindexUtility && title.length > 65) errors.push(`${label}: title length ${title.length}`)
    if (!description) errors.push(`${label}: missing description`)
    else if (!isNoindexUtility && (description.length < 70 || description.length > 170)) errors.push(`${label}: description length ${description.length}`)
    if (description && !isNoindexUtility) descriptions.set(description, [...(descriptions.get(description) ?? []), label])
    if (!canonical) errors.push(`${label}: missing canonical`)
    else {
      if (canonical.origin !== siteOrigin) errors.push(`${label}: canonical has wrong origin ${canonical.href}`)
      if (normalizeRoute(canonical.pathname) !== route) errors.push(`${label}: canonical route mismatch ${canonical.pathname} != ${route}`)
    }
  }

  const jsonLdBlocks = [...html.matchAll(/<script\b[^>]*type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)]
  const skipRichMetadata = !is404 && isTagRoute && isNoindex
  if (!is404 && !skipRichMetadata && jsonLdBlocks.length === 0) errors.push(`${label}: missing JSON-LD`)
  let blogPosting
  for (const match of skipRichMetadata ? [] : jsonLdBlocks) {
    try {
      // Script raw-text content does not use HTML entity decoding.
      const value = JSON.parse(match[1])
      const nodes = Array.isArray(value) ? value : [value]
      const website = nodes.find((node) => node?.["@type"] === "WebSite")
      if (!website || website.description !== stableSiteDescription) errors.push(`${label}: unstable WebSite JSON-LD description`)
      blogPosting = nodes.find((node) => node?.["@type"] === "BlogPosting") ?? blogPosting
      if (blogPosting && (typeof blogPosting.image !== "string" || !blogPosting.image)) errors.push(`${label}: BlogPosting has no image`)
    } catch (error) {
      errors.push(`${label}: invalid JSON-LD (${error.message})`)
    }
  }

  if (!is404 && !skipRichMetadata) {
    const ogType = meta(html, "og:type")
    const ogImage = meta(html, "og:image")
    const twitterImage = meta(html, "twitter:image")
    if (!ogType) errors.push(`${label}: missing og:type`)
    if (!ogImage) errors.push(`${label}: missing og:image`)
    if (!twitterImage) errors.push(`${label}: missing twitter:image`)
    if (blogPosting) {
      if (ogType !== "article") errors.push(`${label}: BlogPosting og:type must be article`)
      if (ogImage !== blogPosting.image) errors.push(`${label}: BlogPosting image differs from og:image`)
      if (twitterImage !== blogPosting.image) errors.push(`${label}: BlogPosting image differs from twitter:image`)
    } else if (ogType && ogType !== "website") {
      errors.push(`${label}: collection/WebSite og:type must be website`)
    }
  }

  const assetRefs = []
  for (const tag of html.match(/<(?:img|source|script|link|video)\b[^>]*>/gi) ?? []) {
    const tagName = tag.match(/^<([a-z]+)/i)?.[1].toLowerCase()
    const direct = attr(tag, tagName === "link" ? "href" : tagName === "video" ? "poster" : "src")
    if (direct) assetRefs.push({ tag, tagName, src: direct })
    const srcset = attr(tag, "srcset")
    if (srcset) for (const entry of srcset.split(",")) {
      const candidate = entry.trim().split(/\s+/, 1)[0]
      if (candidate) assetRefs.push({ tag, tagName, src: candidate })
    }
  }
  for (const { tag, tagName, src } of assetRefs) {
    const asset = localAsset(file, src)
    if (!asset) continue
    if (asset.invalid) { errors.push(`${label}: unsafe or malformed asset path ${src}`); continue }
    if (!fs.existsSync(asset.path)) { errors.push(`${label}: missing asset ${src}`); continue }
    if (/\.(?:png|jpe?g|webp)$/i.test(asset.path)) {
      try { imageDimensions(asset.path) } catch (error) { errors.push(`${label}: ${error.message}`) }
      if (tagName === "img" && (!attr(tag, "width") || !attr(tag, "height"))) errors.push(`${label}: image lacks intrinsic dimensions ${src}`)
    }
  }

  for (const tag of html.match(/<a\b[^>]*>/gi) ?? []) {
    const href = attr(tag, "href")
    if (!href || /^(?:#|mailto:|tel:)/i.test(href)) continue
    if (/^javascript:/i.test(href)) { errors.push(`${label}: unsafe href ${href}`); continue }
    let target
    try { target = new URL(href, canonical ?? currentPageUrl) }
    catch { errors.push(`${label}: malformed href ${href}`); continue }
    if (target.origin !== siteOrigin) continue
    const targetRoute = normalizeRoute(target.pathname)
    if (!targetRoute) { errors.push(`${label}: malformed internal route ${href}`); continue }
    if (/\.[a-z0-9]{2,5}$/i.test(targetRoute)) {
      const asset = localAsset(file, href)
      if (asset?.invalid) errors.push(`${label}: unsafe asset href ${href}`)
      else if (asset && !fs.existsSync(asset.path)) errors.push(`${label}: missing linked asset ${href}`)
      continue
    }
    if (!routes.has(targetRoute)) errors.push(`${label}: missing built route ${href} -> ${targetRoute}`)
  }
}

for (const [description, files] of descriptions) {
  if (files.length > 1) errors.push(`duplicate description (${files.join(", ")}): ${description}`)
}

const sitemapFile = path.join(root, "sitemap.xml")
if (fs.existsSync(sitemapFile)) {
  const sitemap = fs.readFileSync(sitemapFile, "utf8")
  for (const match of sitemap.matchAll(/<loc\b[^>]*>([\s\S]*?)<\/loc>/gi)) {
    const value = decodeHtml(match[1]).trim()
    let location
    try { location = new URL(value) } catch { errors.push(`sitemap.xml: malformed location ${value}`); continue }
    if (location.origin !== siteOrigin) continue
    const sitemapRoute = normalizeRoute(location.pathname)
    if (sitemapRoute && noindexUtilityRoutes.has(sitemapRoute)) {
      errors.push(`sitemap.xml: noindex utility page listed ${location.href}`)
    }
  }
}

for (const file of walk(path.join(root, "assets", "illustrations"), (candidate) => /\.(?:png|jpe?g|webp)$/i.test(candidate))) {
  try { imageDimensions(file) } catch (error) { errors.push(error.message) }
  if (fs.statSync(file).size > 700 * 1024) errors.push(`${path.relative(root, file)} exceeds 700 KiB`)
}

if (errors.length) {
  console.error(
    `built-site validation failed with ${errors.length} issue(s): ${indexableCanonicalPageCount} indexable canonical pages, ${noindexUtilityPageCount} noindex utility pages, ${aliasRedirectCount} alias redirects, ${routes.size} emitted routes`,
  )
  for (const error of errors) console.error(`- ${error}`)
  process.exit(1)
}
console.log(
  `built-site validation passed: ${indexableCanonicalPageCount} indexable canonical pages, ${noindexUtilityPageCount} noindex utility pages, ${aliasRedirectCount} alias redirects, ${routes.size} emitted routes`,
)
