import fs from "node:fs"

const file = process.argv[2]
if (!file) {
  console.error("Usage: node scripts/rewrite-native-graph-assets.mjs <vault-graph.html>")
  process.exit(1)
}

let html = fs.readFileSync(file, "utf8")
html = html
  .replace(/(["'])\.\/index\.css\1/g, "$1./vault-graph.css$1")
  .replace(/(["'])\.\/postscript\.js\1/g, "$1./vault-graph-postscript.js$1")
fs.writeFileSync(file, html)
