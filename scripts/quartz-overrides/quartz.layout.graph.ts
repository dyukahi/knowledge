import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"

export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [],
  afterBody: [],
  footer: Component.Footer({
    links: {
      GitHub: "https://github.com/dyukahi/knowledge",
    },
  }),
}

const NativeVaultGraph = Component.Graph({
  localGraph: {
    depth: -1,
    scale: 0.9,
    repelForce: 0.7,
    centerForce: 0.22,
    linkDistance: 36,
    fontSize: 0.7,
    opacityScale: 1,
    showTags: false,
    focusOnHover: true,
    enableRadial: true,
  },
  globalGraph: {
    depth: -1,
    scale: 0.9,
    repelForce: 0.7,
    centerForce: 0.22,
    linkDistance: 36,
    fontSize: 0.7,
    opacityScale: 1,
    showTags: false,
    focusOnHover: true,
    enableRadial: true,
  },
})

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [Component.ArticleTitle(), Component.ContentMeta(), Component.TagList(), NativeVaultGraph],
  left: [Component.PageTitle(), Component.Search(), Component.Darkmode()],
  right: [],
}

export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.ArticleTitle(), NativeVaultGraph],
  left: [Component.PageTitle(), Component.Search(), Component.Darkmode()],
  right: [],
}
