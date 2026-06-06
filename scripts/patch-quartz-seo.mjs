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
console.log(`Applied redpill.wiki SEO patch to ${quartzRoot}`)
