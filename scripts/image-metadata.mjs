import fs from "node:fs"

function svgNumber(value) {
  if (!value || !/^\s*(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?(?:px)?\s*$/i.test(value)) return null
  const number = Number.parseFloat(value)
  return Number.isFinite(number) && number > 0 ? number : null
}

function svgDimensions(data, file) {
  const source = data.toString("utf8").replace(/<!--[\s\S]*?-->/g, "")
  const root = source.match(/<svg\b(?:[^"'<>]|"[^"]*"|'[^']*')*>/i)?.[0]
  if (!root) throw new Error(`corrupt SVG: ${file}`)

  const attribute = (name) => root.match(new RegExp(`(?:^|\\s)${name}\\s*=\\s*(["'])(.*?)\\1`, "i"))?.[2]
  let width = svgNumber(attribute("width"))
  let height = svgNumber(attribute("height"))
  const viewBox = attribute("viewBox")?.trim().split(/[\s,]+/).map(Number)
  const viewBoxWidth = viewBox?.length === 4 && Number.isFinite(viewBox[2]) && viewBox[2] > 0 ? viewBox[2] : null
  const viewBoxHeight = viewBox?.length === 4 && Number.isFinite(viewBox[3]) && viewBox[3] > 0 ? viewBox[3] : null

  if (viewBoxWidth && viewBoxHeight) {
    if (width && !height) height = width * viewBoxHeight / viewBoxWidth
    else if (height && !width) width = height * viewBoxWidth / viewBoxHeight
    else if (!width && !height) ({ width, height } = { width: viewBoxWidth, height: viewBoxHeight })
  }
  if (!width || !height) throw new Error(`SVG lacks usable intrinsic dimensions: ${file}`)
  return { width, height, type: "svg" }
}

export function imageDimensions(file) {
  const data = fs.readFileSync(file)
  if (/\.svg$/i.test(file)) return svgDimensions(data, file)
  if (data.length >= 24 && data.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) {
    return { width: data.readUInt32BE(16), height: data.readUInt32BE(20), type: "png" }
  }
  if (data.length >= 12 && data.toString("ascii", 0, 4) === "RIFF" && data.toString("ascii", 8, 12) === "WEBP") {
    const kind = data.toString("ascii", 12, 16)
    if (kind === "VP8X" && data.length >= 30) return { width: 1 + data.readUIntLE(24, 3), height: 1 + data.readUIntLE(27, 3), type: "webp" }
    if (kind === "VP8 " && data.length >= 30 && data.subarray(23, 26).equals(Buffer.from([157, 1, 42]))) return { width: data.readUInt16LE(26) & 0x3fff, height: data.readUInt16LE(28) & 0x3fff, type: "webp" }
    if (kind === "VP8L" && data.length >= 25 && data[20] === 0x2f) {
      const bits = data.readUInt32LE(21)
      return { width: (bits & 0x3fff) + 1, height: ((bits >>> 14) & 0x3fff) + 1, type: "webp" }
    }
    throw new Error(`corrupt or unsupported WebP: ${file}`)
  }
  if (data.length >= 4 && data[0] === 0xff && data[1] === 0xd8) {
    let offset = 2
    const sof = new Set([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf])
    while (offset + 9 < data.length) {
      if (data[offset] !== 0xff) { offset++; continue }
      const marker = data[offset + 1]
      offset += 2
      if (marker === 0xd8 || marker === 0xd9 || (marker >= 0xd0 && marker <= 0xd7)) continue
      if (offset + 2 > data.length) break
      const size = data.readUInt16BE(offset)
      if (sof.has(marker)) return { width: data.readUInt16BE(offset + 5), height: data.readUInt16BE(offset + 3), type: "jpeg" }
      if (size < 2) break
      offset += size
    }
    throw new Error(`corrupt JPEG: ${file}`)
  }
  throw new Error(`unsupported or corrupt image: ${file}`)
}
