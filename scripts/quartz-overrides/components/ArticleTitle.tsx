import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"

type HastNode = {
  type?: string
  tagName?: string
  children?: HastNode[]
}

function containsH1(node: HastNode | undefined): boolean {
  if (!node) return false
  if (node.type === "element" && node.tagName === "h1") return true
  return Array.isArray(node.children) && node.children.some(containsH1)
}

const ArticleTitle: QuartzComponent = ({ fileData, displayClass, tree }: QuartzComponentProps) => {
  const title = fileData.frontmatter?.title
  if (!title || containsH1(tree as HastNode)) {
    return null
  } else {
    return <h1 class={classNames(displayClass, "article-title")}>{title}</h1>
  }
}

ArticleTitle.css = `
.article-title {
  margin: 2rem 0 0 0;
}
`

export default (() => ArticleTitle) satisfies QuartzComponentConstructor
