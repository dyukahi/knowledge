import { PageLayout, SharedLayout } from "./quartz/cfg"
import * as Component from "./quartz/components"
import type { QuartzComponent } from "./quartz/components/types"

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
    scale: 2.1,
    repelForce: 1.15,
    centerForce: 0.32,
    linkDistance: 58,
    fontSize: 0.85,
    opacityScale: 1,
    showTags: false,
    focusOnHover: true,
    enableRadial: true,
  },
  globalGraph: {
    depth: -1,
    scale: 2.1,
    repelForce: 1.15,
    centerForce: 0.32,
    linkDistance: 58,
    fontSize: 0.85,
    opacityScale: 1,
    showTags: false,
    focusOnHover: true,
    enableRadial: true,
  },
})

const GraphPageStyles: QuartzComponent = () => null
GraphPageStyles.css = `
body[data-slug="vault-graph"] .page {
  max-width: none !important;
  width: 100vw !important;
  margin: 0 !important;
}
body[data-slug="vault-graph"] #quartz-body {
  grid-template: "grid-header" "grid-center" / minmax(0, 1fr) !important;
  grid-template-columns: minmax(0, 1fr) !important;
  column-gap: 0 !important;
}
body[data-slug="vault-graph"] .left.sidebar,
body[data-slug="vault-graph"] .right.sidebar,
body[data-slug="vault-graph"] footer,
body[data-slug="vault-graph"] .content-meta,
body[data-slug="vault-graph"] .tags,
body[data-slug="vault-graph"] main#main-content {
  display: none !important;
}
body[data-slug="vault-graph"] .center {
  grid-area: grid-center !important;
  max-width: none !important;
  width: 100vw !important;
  margin: 0 !important;
  padding: 1rem clamp(1rem, 2vw, 2rem) !important;
}
body[data-slug="vault-graph"] .page-header {
  grid-area: grid-header !important;
  margin: 0 !important;
  width: 100% !important;
}
body[data-slug="vault-graph"] .popover-hint {
  width: 100% !important;
}
body[data-slug="vault-graph"] .page-header > .popover-hint > h1 {
  margin: 0 0 0.75rem !important;
  font-size: clamp(1.4rem, 2.5vw, 2.4rem) !important;
}
body[data-slug="vault-graph"] .graph {
  width: 100% !important;
  margin: 0 !important;
}
body[data-slug="vault-graph"] .graph > h3 {
  position: absolute;
  inline-size: 1px;
  block-size: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
}
body[data-slug="vault-graph"] .graph-outer {
  width: 100% !important;
  height: calc(100vh - 4.25rem) !important;
  min-height: 680px !important;
  border: 1px solid var(--lightgray) !important;
  border-radius: 14px !important;
  overflow: hidden !important;
  background: color-mix(in srgb, var(--light) 88%, transparent) !important;
}
body[data-slug="vault-graph"] .graph-container {
  width: 100% !important;
  height: 100% !important;
  min-height: inherit !important;
}
body[data-slug="vault-graph"] .global-graph-icon,
body[data-slug="vault-graph"] .global-graph-outer {
  display: none !important;
}
body[data-slug="vault-graph"] canvas {
  max-width: none !important;
}
@media (max-width: 800px) {
  body[data-slug="vault-graph"] .center {
    padding: 0.75rem !important;
  }
  body[data-slug="vault-graph"] .graph-outer {
    height: calc(100vh - 3.75rem) !important;
    min-height: 560px !important;
    border-radius: 10px !important;
  }
}
`

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [Component.ArticleTitle(), GraphPageStyles, NativeVaultGraph],
  left: [Component.PageTitle(), Component.Search(), Component.Darkmode()],
  right: [],
}

export const defaultListPageLayout: PageLayout = {
  beforeBody: [Component.ArticleTitle(), GraphPageStyles, NativeVaultGraph],
  left: [Component.PageTitle(), Component.Search(), Component.Darkmode()],
  right: [],
}
