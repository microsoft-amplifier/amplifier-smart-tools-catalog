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

The inventory remains `tools/*/source.json`. Optional root `domains.json` contains `{"domains": [...]}`, with each domain recording a stable string `id`, a nonempty string `label`, and a nonempty string `scope`. IDs are unique. Domain additions, label changes, and scope changes are catalog review decisions, not upstream declarations.

Optional `tools/<slug>/listing.json` records one primary approved domain and a boolean recommendation designation:

```json
{
  "domain": "test-environments",
  "recommended": true,
  "reviewed_source": {
    "repository": "https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe.git",
    "path": ".",
    "commit": "900583d3bc40ea8c6363a9b53c2560a0cdc98b74"
  }
}
```

This example records the DTU revision in the catalog's October 7 snapshot; it is not a current-health or certification claim. DTU and Smart Tool Creator remain initial choices included for Brian/Sam decision before merge; no confirmation of selection or approval is claimed by their unmerged true seed metadata. `domain` must identify a domain in this catalog's registry. `recommended` is a required boolean. When true, `reviewed_source` requires a credential-free HTTPS repository URL, a safe relative POSIX distribution path, and a full source commit. Repository, path, and commit are separate identity fields. An ordinary classified entry uses `recommended: false` and must not carry a reviewed source. Missing listing metadata means listed, unclassified, and not recommended; missing metadata preserves legacy discovery.

There may be at most one recommendation designation per domain. A designation that needs review still counts. Contributors submit source pointers and optional ordinary classification, not recommendation nominations. Do not solicit recommendation requests or proposals from authors. Only Brian or Sam chooses the tool, domain, and source revision and initiates designations, renewals, replacements, and withdrawals; either one may decide. They select and initiate, rather than approve everyone's nominations. Contributors or agents may edit metadata only to implement their explicit decision; an arbitrary author's "make mine recommended" request or PR authorship cannot authorize it. Record the decision, rationale, and actual evidence as described in the [contribution rules](../README.md#editorial-approval). Domain additions, label changes, and scope changes separately require Brian or Sam's review and approval; a contributor cannot create a tool-specific domain to evade the limit. The optional true format and structural checks do not establish selection authority; documentation alone does not prove GitHub enforces these rules.

Effective recommendation requires agreement between reviewed source, source pointer, and snapshot provenance on repository, distribution path, and commit. Readers honor the pointer's requested or default ref, including a full commit pin, and do not treat an obsolete pointer/provenance pairing as effective. They read registry, listing, pointer, and snapshot from one resolved catalog revision. Well-formed metadata whose identity has drifted remains valid editorial data, but displays “Recommendation needs review” and confers no recommendation preference. Malformed metadata fails validation and cannot create an endorsement.

Automatic refresh writes only generated snapshot and provenance files. It must preserve `domains.json`, every `listing.json`, and reviewed commits byte for byte after successful, failed, or partially successful refresh. Renewal, withdrawal, and replacement are deliberate editorial changes, never refresh side effects. Upstream manifests and source pointers cannot grant a catalog recommendation.

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
- Missing editorial metadata preserves listing and discovery; known domains and correctly typed sidecars validate through the canonical shared validator.
- Unknown domains, malformed metadata, invalid reviewed identities, and a second recommendation designation in one domain fail validation.
- Refresh preserves editorial files byte for byte, and source drift cannot silently renew an endorsement.
