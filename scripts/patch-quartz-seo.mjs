import fs from "node:fs"
import path from "node:path"

const quartzRoot = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd()
const repoRoot = path.resolve(new URL("..", import.meta.url).pathname.replace(/^\/(.:\/)/, "$1"))
const overridesRoot = path.join(repoRoot, "scripts", "quartz-overrides")
const copies = [
  [path.join(overridesRoot, "quartz.layout.ts"), path.join(quartzRoot, "quartz.layout.ts")],
  [path.join(overridesRoot, "components", "Head.tsx"), path.join(quartzRoot, "quartz", "components", "Head.tsx")],
  [path.join(overridesRoot, "components", "ArticleTitle.tsx"), path.join(quartzRoot, "quartz", "components", "ArticleTitle.tsx")],
  [path.join(overridesRoot, "util", "glob.ts"), path.join(quartzRoot, "quartz", "util", "glob.ts")],
]

for (const [src, dest] of copies) {
  if (!fs.existsSync(src)) throw new Error(`Missing override: ${src}`)
  if (!fs.existsSync(dest)) throw new Error(`Missing Quartz target: ${dest}`)
  fs.copyFileSync(src, dest)
  console.log(`patched ${path.relative(quartzRoot, dest)}`)
}

// Quartz constrains article images with max-width but does not reset the HTML
// height presentation hint. Once intrinsic width/height are added for CLS, a
// narrow container otherwise scales only the width and visibly distorts images.
const baseStyles = path.join(quartzRoot, "quartz", "styles", "base.scss")
const imageRuleBefore = `img {
  max-width: 100%;
  border-radius: 5px;`
const imageRuleAfter = `img {
  max-width: 100%;
  height: auto;
  border-radius: 5px;`
if (!fs.existsSync(baseStyles)) throw new Error(`Missing Quartz target: ${baseStyles}`)
const baseSource = fs.readFileSync(baseStyles, "utf8")
if (baseSource.includes(imageRuleAfter)) {
  console.log(`responsive image sizing already present in ${path.relative(quartzRoot, baseStyles)}`)
} else if (baseSource.includes(imageRuleBefore)) {
  fs.writeFileSync(baseStyles, baseSource.replace(imageRuleBefore, imageRuleAfter), "utf8")
  console.log(`patched responsive image sizing in ${path.relative(quartzRoot, baseStyles)}`)
} else {
  throw new Error("Quartz base image rule changed; refusing an unverified CSS patch")
}

console.log(`Applied redpill.wiki SEO patch to ${quartzRoot}`)
