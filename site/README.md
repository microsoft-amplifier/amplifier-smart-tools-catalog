# Website

This repository's promotional page uses the Amplifier Smart Tools family theme.
Product page content lives in `site.json`. The canonical theme is maintained in
`microsoft/amplifier-smart-tools/site/theme`; this repository carries a versioned
copy so a build does not depend on a moving remote theme or an online service.
Theme version: 0.1.0. Theme code is MIT licensed.

## Build and preview

From the repository root, using Python 3.12 or later:

```sh
python3 -m venv .work/site-venv
.work/site-venv/bin/python -m pip install -r site/requirements.txt
.work/site-venv/bin/python site/theme/build.py --family-owner robotdad
python3 -m http.server 8000 --directory _site --bind 127.0.0.1
```

Open http://127.0.0.1:8000. Generated output belongs in `_site/` and is ignored.
The site is a static build; visitors need no Python runtime or account.

The `--family-owner robotdad` option points overview and catalog links at the
fork previews. Omit it for their Microsoft organization URLs. Individual tool
links retain their authors' owners. Keep the same setting across the family.
For a combined local preview, build each page with `--local --output` into a
shared preview directory named after its repository, then serve that directory.

## GitHub Pages

The Website workflow builds a `github-pages` artifact for relevant pull requests and retains it for seven days. See the root [preview instructions](../README.md#review-a-website-preview) for downloading the exact run's `artifact.tar` and serving the static build. Pull requests never deploy.

On main, relevant pushes build and publish automatically. Either success or failure of a trusted Refresh Amplifier Smart Tools manifests run on main also triggers a validated build and publish from current main, including successful entry updates committed during a partially failed refresh. The workflow never consumes triggering-run code or artifacts. Metadata validation belongs to the canonical renderer and is also run by CI through `scripts/validate_catalog.py`.

The existing GitHub Actions Pages setup and main environment policy remain unchanged. Manual publication is restricted to main; other revisions are preview-only. All linked family sites must be published before cross-site navigation is live.

## Shared identity

Use the full family name, Amplifier Smart Tools, as one masthead and footer
identity. The overview explains the format and how to build a tool; discovery
and individual tool listings belong in the catalog.

Use plain punctuation, with middle dots permitted between Math, AI, Design, and
Engineering in the team name. Keep MADE and Microsoft Office of the CTO as text
attribution. Do not link to the internal team site. Preserve the shared navigation,
layout, typography, paper background, and gold details; a tool may set its own
accent, content, and image in `site.json`.

Images are copied from the repository's existing `docs/images/` at build time.
Their existing provenance remains there. Screenshots are labeled as screenshots;
concept artwork is labeled as illustration. Add demo video only when reviewed
footage is available. Do not use a fake player over a still image.

To update a vendored theme, run the canonical `site/sync_theme.py` with an explicit
target checkout, review the diff, and build again. It updates only `site/theme/`.
Page content stays in the owning repository. The family link registry holds only
navigation identity; the catalog's tool inventory remains `tools/*/source.json`.

## Motion assets

The shared title mark uses an eight-second looping GIF with a static PNG fallback.
The overview illustration has a pause control that also pauses its title mark. Reduced-motion
preferences select the still image by default. Shared media lives in
`site/theme/assets/` and is included by the theme sync script. The original briefs
and generation provenance live in `amplifier-smart-tools/site/artwork/`.

## Catalog categories and Recommended

The catalog uses the flat `categories.json` taxonomy and each listing's optional
primary `category`. Keep category IDs stable and expose labels and scopes without
turning categories into a hierarchy. Ordinary and not-yet-classified listings
remain available.

Each card shows its “Category: {label}” prefix. Effective recommendations use a plain, noninteractive “Recommended” badge; designations needing review retain the separate “Recommendation needs review” badge. Ordinary listings have no recommendation-status badge. Cards without listings show “Category: Not yet classified.”

The current data classifies all 22 tools across nine categories: two effective recommendations, 20 ordinary listings, and zero unclassified tools. The seven category additions and assignments are proposed for maintainer review, not already approved. See the root [category table](../README.md#categories-and-recommendations) for coverage; category scopes remain in `categories.json`. Missing classification is still valid for future source-pointer contributions, not an expected gap in the current 22-tool inventory.

Explain “Recommended” as a maintainer-curated preference for a category at a selected recorded source revision under the [maintainer guide](../docs/maintainers.md). It is not certification, guaranteed outcomes, or proof of local readiness. Catalog metadata tests do not establish tool quality or completed evaluation.

Keep Recommended separate from All tools. Render each effective recommendation once in the Recommended region as a shortcut and once in All tools; its category label remains on both cards, but the featured shortcut uses the section heading instead of a redundant “Recommended” badge. All tools includes all 22 unique listings, so the two regions render 24 card instances in total. Hide the entire Recommended region when its effective matching count is zero, including on the initial no-JavaScript page when no designation is effective. Do not render a Recommended empty-state message, recommendation-specific details disclosure, or explanation link. The badge is static text, not a control. Existing optional “Full description and source” details retain source provenance and refresh information.

Show the selected recorded revision separately from snapshot provenance and refresh time. Retain the `reviewed_source` field name for schema compatibility: it records selected source identity, not proof of conformance or task results. Source drift removes recommendation preference without removing the category or listing. The stale designation still occupies its category's slot. Digital Twin Universe and Smart Tool Creator are effective recommendations for Test environments and Smart Tool development respectively.

Render the two effective recommendation shortcuts in Recommended before All tools, and also include both listings in the complete All tools list. Group all 22 unique listings, including the recommendations, into their populated categories; do not create empty category groups. Keep every card's category label. Search matches displayed tool names and category labels.

Use one control bar above all results: Search, Category, Platform, Sort by (Category or Name), and one Clear filters action. Search, category, and platform filter both copies; sorting changes All tools only. Do not display category scope text or insert it on selection; keep scope metadata in the registry. Include “Not yet classified” only when an unclassified entry exists. At phone widths, Search spans a row, Category and Platform share a two-column row, and Sort by and Clear filters share the next row. Keep the native selects at a stable height and min-width 0; keep Clear filters at least 44px tall. The `tool-sort` select defaults to Category. Name places all 22 unique listings in one globally alphabetical list; Category restores their category groups. Recommended remains separate in either mode, and clearing filters preserves the selected sort.

All filter controls remain hidden without JavaScript so all 22 unique listings stay visible in All tools, alongside the two featured shortcuts (24 rendered cards). The global and All tools counts report unique listings, not rendered card instances. The category headings are noninteractive and there is no separate category-navigation panel.

Keep review evidence free of credentials and private details. Preserve public
source URLs and exact generated manifests. Implement shared rendering and
metadata changes in the canonical theme, then sync; never patch the vendored
copy independently.
