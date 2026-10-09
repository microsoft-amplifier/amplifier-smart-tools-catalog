# Catalog Source Contract - v1 (DRAFT)

**Who builds against this** Catalog contributors and consumers that read source
pointers, including the shared `amplifier-smart-tools` skill.

## What it looks like

A contributor adds one folder. The source pointer can float on main or identify
a specific revision without describing the tool a second time.

```text
tools/tmux/source.json
```

```json
{
  "repository": "https://github.com/microsoft/amplifier-smart-tool-tmux.git",
  "ref": "9a4a167101c92b803f7a693e6614a21a6d21cf5b"
}
```

## Purpose

Contributors and readers agree on where a tool comes from.
Defaults cannot silently change a lookup's meaning.
The catalog preserves the upstream tool as the owner of its description.

## Core (the teeth)

1. **The inventory is folder-based.** Entries live at `tools/<slug>/source.json`.
   Readers enumerate that directory without requiring a top-level inventory.
2. **A source pointer identifies a repository and optional location.**
   `repository` is a required HTTPS Git URL. Optional string `ref` identifies
   a branch, tag, or full commit SHA. Optional string `path` identifies the
   distribution root containing `smart-tool.json`.
3. **Omission has explicit defaults.** Missing `ref` means exactly `main`.
   Missing `path` means `.`. An unavailable main branch is an error, not a
   reason to substitute the repository's default branch.
4. **Revision and URL are separate.** `repository` uses HTTPS Git notation,
   not an installer-specific `git+https` URL containing a revision.
5. **A lookup uses one resolved commit.** A branch or tag is resolved once for
   each inspected source per discovery operation. Descriptor and manifest
   are read from that same commit. A full commit pin is honored.
6. **Provenance is reported.** Readers identify the repository, distribution
   path, requested or default ref, and resolved commit used for the lookup.
7. **The tool owns the manifest.** Readers follow upstream `smart-tool.json` to `SMART_TOOL.md`. The only permitted copy of a tool description is an exact generated `SMART_TOOL.md` snapshot plus provenance recording its source and refresh time. Catalog-owned `listing.json` is editorial metadata, not an independently written or maintained tool description.
8. **A failed lookup is visible.** An inaccessible repository, unresolved ref,
   or missing descriptor or manifest produces a specific blocker for that
   entry, not invented metadata or a silent switch to another source.

## Optional catalog editorial metadata

The inventory remains `tools/*/source.json`. Optional root `categories.json` contains `{"categories": [...]}`, with each category recording a stable string `id`, a nonempty string `label`, and a nonempty string `scope`. The taxonomy is flat and IDs are unique. Category additions, label changes, and scope changes require separate maintainer review and approval, not upstream declarations. IDs remain stable when labels change.

Optional `tools/<slug>/listing.json` records one primary approved category and a boolean recommendation designation:

```json
{
  "category": "test-environments",
  "recommended": false
}
```

This example is an ordinary classified listing, not a recommendation. DTU and Smart Tool Creator remain initial choices pending recorded review evidence, with `recommended: false` and no `reviewed_source`; this does not imply either tool failed. `category` must identify a category in this catalog's registry. `recommended` is a required boolean. When true, `reviewed_source` requires a credential-free HTTPS repository URL, a safe relative POSIX distribution path, and a full source commit. Repository, path, and commit are separate identity fields. `reviewed_source` is identity metadata, neither an installer nor certification. An ordinary classified entry uses `recommended: false` and must not carry a reviewed source. Missing listing metadata means listed, unclassified, and not recommended; missing metadata preserves legacy discovery.

There may be at most one primary category per listing and one recommendation designation per category. A designation that needs review still counts. Contributors submit source pointers and optional ordinary classification, not recommendation nominations. Only catalog maintainers select tools, categories, and source revisions and initiate designations, renewals, replacements, and withdrawals. Contributors or agents may edit metadata only to implement an explicit maintainer decision; a creator request or PR authorship cannot authorize it. The [maintainer guide](../docs/maintainers.md) is normative: before merge, a designation, renewal, or replacement requires a recorded maintainer review status, decision, rationale, and evidence of conformance review and representative task scenarios, including exact revisions, PASS/SKIP results, environment, provider setup, inputs, expected and observed outcomes, and scope limitations. Evidence belongs in the PR or repository maintainer notes, not duplicate sidecar fields. Metadata validation does not evaluate tool quality, establish selection authority, or prove GitHub enforcement. Recommendation is revision-scoped editorial judgment, not certification, guaranteed outcomes, or local readiness.

Effective recommendation requires agreement between reviewed source, source pointer, and snapshot provenance on repository, distribution path, and commit. Readers honor the pointer's requested or default ref, including a full commit pin, and do not treat an obsolete pointer/provenance pairing as effective. They read registry, listing, pointer, and snapshot from one resolved catalog revision. Well-formed metadata whose identity has drifted remains valid editorial data, but displays “Recommendation needs review” and confers no recommendation preference. Malformed metadata fails validation and cannot create an endorsement.

Automatic refresh writes only generated snapshot and provenance files. It must preserve `categories.json`, every `listing.json`, and reviewed commits byte for byte after successful, failed, or partially successful refresh. Renewal, withdrawal, and replacement are deliberate editorial changes, never refresh side effects. Upstream manifests and source pointers cannot grant a catalog recommendation.

## What v1 deliberately does NOT freeze

- Fetch library or GitHub API choice - reconsider when a transport limits use.
- Search summaries beyond exact generated manifest snapshots - reconsider when
  measured catalog size, latency, or offline use makes them necessary.
- Installation mechanisms remain owned by the tool and existing host tooling.
  This catalog does not ship an installer.

## Observable behavior

These criteria describe correctness, not a validation-kit deliverable or a
claim that checks have passed.

- Omitted fields resolve to main and the root; explicit nested paths work.
- A full commit pin is preserved and a moving branch is resolved only once.
- An unavailable main does not fall back to another branch.
- Descriptor and manifest provenance contains the same resolved commit.
- Missing source artifacts produce named blockers rather than substituted data.
- Generated snapshots, when present, preserve the upstream manifest bytes and
  record the repository, requested ref, distribution path, resolved commit,
  original manifest path, and successful refresh time.
- Missing editorial metadata preserves listing and discovery; known categories and correctly typed sidecars validate through the canonical shared validator.
- Unknown categories, malformed metadata, invalid reviewed identities, and a second recommendation designation in one category fail validation.
- Refresh preserves editorial files byte for byte, and source drift cannot silently renew an endorsement.
