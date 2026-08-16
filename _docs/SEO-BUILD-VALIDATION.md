# SEO Build Validation

The repository does not vendor Quartz or its dependencies. GitHub Actions checks out
`jackyzha0/quartz` at `v4`, copies this vault into `quartz/content`, applies the
tracked overrides, installs with `npm ci`, and builds both the normal site and the
isolated vault graph page.

After both builds, CI runs:

```sh
python3 content/scripts/optimize-images.py --check
node content/scripts/patch-built-image-dimensions.mjs quartz/public
node content/scripts/validate-built-site.mjs quartz/public
```

The image check rejects oversized PNG/JPEG source illustrations. The post-build
patch reads PNG, JPEG, and WebP headers directly and adds intrinsic `width` and
`height` to raster `<img>` elements; it ignores remote/data images and SVGs. The
validator then fails the job for missing built routes, missing or invalid metadata,
duplicate descriptions, invalid JSON-LD, missing/corrupt/oversized illustration
assets, or raster content images without intrinsic dimensions. Route comparisons
use emitted HTML routes plus normalized NFC Unicode and percent-decoded URL paths.

To reproduce locally, provide a Quartz v4 checkout as the workflow does, build it,
then pass its output directory to the two Node scripts. No network request is used
by validation: internal links are checked against the actual emitted route set.
