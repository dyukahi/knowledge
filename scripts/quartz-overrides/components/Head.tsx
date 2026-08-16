import { i18n } from "../i18n"
import { FullSlug, getFileExtension, joinSegments, pathToRoot } from "../util/path"
import { CSSResourceToStyleElement, JSResourceToScriptElement } from "../util/resources"
import { googleFontHref, googleFontSubsetHref } from "../util/theme"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { unescapeHTML } from "../util/escape"
import type { Element, Root } from "hast"

const SITE_DESCRIPTION =
  "Red Pill Wiki là kho tri thức độc lập về tư duy phản biện, chủ quyền cá nhân, lịch sử, khoa học, tài chính và ý thức."

function cleanBaseUrl(baseUrl: string | undefined): string {
  const configured = baseUrl ?? "redpill.wiki"
  return configured.replace(/^https?:\/\//, "").replace(/\/+$/, "")
}

function pageUrl(baseUrl: string, slug: string | undefined): string {
  const root = `https://${baseUrl}`
  if (!slug || slug === "index" || slug === "404") return `${root}/`
  const normalizedSlug = slug.replace(/^\/+|\/+$/g, "")
  if (normalizedSlug.endsWith("/index")) return `${root}/${normalizedSlug.slice(0, -"index".length)}`
  return `${root}/${normalizedSlug}`
}

function toIsoDate(value: unknown): string | undefined {
  if (!value) return undefined
  const date = value instanceof Date ? value : new Date(String(value))
  if (Number.isNaN(date.getTime())) return undefined
  return date.toISOString()
}

function compactObject<T extends Record<string, unknown>>(obj: T): T {
  return Object.fromEntries(Object.entries(obj).filter(([, value]) => value !== undefined && value !== null && value !== "")) as T
}

function schemaTypeFor(fileData: QuartzComponentProps["fileData"]): "WebSite" | "CollectionPage" | "BlogPosting" {
  if (fileData.slug === "index") return "WebSite"
  const slug = String(fileData.slug ?? "")
  const tags = Array.isArray(fileData.frontmatter?.tags) ? fileData.frontmatter?.tags.map(String) : []
  const pageTitle = String(fileData.frontmatter?.title ?? "")
  const isCollection = slug.endsWith("index") || slug.startsWith("tags/") || slug.startsWith("folder/") || tags.some((tag) => /(^|-)moc($|-)|index|hub|glossary/i.test(tag)) || /^(MOC\b|Glossary\b|.*Từ Điển.*)/i.test(pageTitle)
  return isCollection ? "CollectionPage" : "BlogPosting"
}

function firstArticleImage(tree: Root, canonicalUrl: string): string | undefined {
  const queue = [...tree.children]
  while (queue.length > 0) {
    const node = queue.shift()
    if (!node || node.type !== "element") continue
    const element = node as Element
    if (element.tagName === "img") {
      const src = String(element.properties?.src ?? "")
      if (src && !src.startsWith("data:") && !/\.(?:svg)(?:[?#]|$)/i.test(src)) {
        try {
          const resolved = new URL(src, canonicalUrl)
          if (resolved.protocol === "http:" || resolved.protocol === "https:") return resolved.href
        } catch {
          // Ignore malformed image URLs and continue to the next representative image.
        }
      }
    }
    queue.unshift(...element.children)
  }
  return undefined
}

export default (() => {
  const Head: QuartzComponent = ({
    cfg,
    fileData,
    tree,
    externalResources,
  }: QuartzComponentProps) => {
    const plainTitle = String(fileData.frontmatter?.title ?? i18n(cfg.locale).propertyDefaults.title)
    const titleSuffix = cfg.pageTitleSuffix ?? ""
    const title = (plainTitle + titleSuffix).length <= 65 ? plainTitle + titleSuffix : plainTitle
    const description =
      fileData.frontmatter?.socialDescription ??
      fileData.frontmatter?.description ??
      unescapeHTML(fileData.description?.trim() ?? i18n(cfg.locale).propertyDefaults.description)

    const { css, js, additionalHead } = externalResources

    const normalizedBaseUrl = cleanBaseUrl(cfg.baseUrl)
    const url = new URL(`https://${normalizedBaseUrl}`)
    const path = url.pathname as FullSlug
    const baseDir = fileData.slug === "404" ? path : pathToRoot(fileData.slug!)
    const iconPath = joinSegments(baseDir, "static/icon.png")

    const canonicalUrl = pageUrl(normalizedBaseUrl, fileData.slug)
    const socialUrl = canonicalUrl
    const slug = String(fileData.slug ?? "")
    const isTagPage = slug === "tags" || slug.startsWith("tags/")

    const ogImageDefaultPath = `https://${normalizedBaseUrl}/static/og-image.png`

    const schemaType = schemaTypeFor(fileData)
    const published = toIsoDate(fileData.frontmatter?.published ?? fileData.frontmatter?.date ?? fileData.dates?.published ?? fileData.dates?.created)
    const modified = toIsoDate(fileData.frontmatter?.modified ?? fileData.dates?.modified)
    const websiteSchema = compactObject({
      "@context": "https://schema.org",
      "@type": "WebSite",
      "@id": `https://${normalizedBaseUrl}/#website`,
      url: `https://${normalizedBaseUrl}/`,
      name: cfg.pageTitle,
      description: SITE_DESCRIPTION,
      inLanguage: cfg.locale,
    })
    const articleImage = firstArticleImage(tree, canonicalUrl) ?? ogImageDefaultPath
    const socialImage = schemaType === "BlogPosting" ? articleImage : ogImageDefaultPath
    const pageSchema = schemaType === "WebSite" ? websiteSchema : compactObject({
      "@context": "https://schema.org",
      "@type": schemaType,
      "@id": `${canonicalUrl}#webpage`,
      url: canonicalUrl,
      isPartOf: { "@id": `https://${normalizedBaseUrl}/#website` },
      headline: plainTitle,
      name: plainTitle,
      description,
      inLanguage: cfg.locale,
      datePublished: published,
      dateModified: modified ?? published,
      image: schemaType === "BlogPosting" ? articleImage : ogImageDefaultPath,
    })
    const jsonLd = JSON.stringify(schemaType === "WebSite" ? websiteSchema : [websiteSchema, pageSchema])

    return (
      <head>
        <title>{title}</title>
        <meta charSet="utf-8" />
        {cfg.theme.cdnCaching && cfg.theme.fontOrigin === "googleFonts" && (
          <>
            <link rel="preconnect" href="https://fonts.googleapis.com" />
            <link rel="preconnect" href="https://fonts.gstatic.com" />
            <link rel="stylesheet" href={googleFontHref(cfg.theme)} />
            {cfg.theme.typography.title && (
              <link rel="stylesheet" href={googleFontSubsetHref(cfg.theme, cfg.pageTitle)} />
            )}
          </>
        )}
        <link rel="preconnect" href="https://cdnjs.cloudflare.com" crossOrigin="anonymous" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />

        <link rel="canonical" href={canonicalUrl} />
        {isTagPage && <meta name="robots" content="noindex,follow" />}
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: jsonLd }} />

        <meta name="og:site_name" content={cfg.pageTitle}></meta>
        <meta property="og:title" content={title} />
        <meta property="og:type" content={schemaType === "BlogPosting" ? "article" : "website"} />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={title} />
        <meta name="twitter:description" content={description} />
        <meta property="og:description" content={description} />
        <meta property="og:image:alt" content={description} />

        <meta property="og:image" content={socialImage} />
        <meta property="og:image:url" content={socialImage} />
        <meta name="twitter:image" content={socialImage} />
        <meta
          property="og:image:type"
          content={`image/${getFileExtension(new URL(socialImage).pathname) ?? "png"}`}
        />

        {cfg.baseUrl && (
          <>
            <meta property="twitter:domain" content={normalizedBaseUrl}></meta>
            <meta property="og:url" content={socialUrl}></meta>
            <meta property="twitter:url" content={socialUrl}></meta>
          </>
        )}

        <link rel="icon" href={iconPath} />
        <meta name="description" content={description} />
        <meta name="generator" content="Quartz" />

        {css.map((resource) => CSSResourceToStyleElement(resource, true))}
        {js
          .filter((resource) => resource.loadTime === "beforeDOMReady")
          .map((res) => JSResourceToScriptElement(res, true))}
        {additionalHead.map((resource) => {
          if (typeof resource === "function") {
            return resource(fileData)
          } else {
            return resource
          }
        })}
      </head>
    )
  }

  return Head
}) satisfies QuartzComponentConstructor
