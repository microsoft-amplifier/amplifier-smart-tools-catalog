# Repository working rules

Read `docs/VISION.md` and the relevant contract in `contracts/` before changing
product behavior. Draft status is not evidence of approval or working software.
Read `docs/maintainers.md` for the normative maintainer curation policy and suggested evaluation practice.

## What belongs here

- Commit settled product outputs and durable repo guidance.
- Keep temporary design drafts, session plans, agent thinking, return logs,
  and workflow bookkeeping in the surrounding workspace, not this repository.
- Do not copy workspace working documents into the repo as context.

## Keep it small

- The skill that reads this catalog is `amplifier-smart-tools`, maintained in
  `microsoft/amplifier-smart-tools`. Do not add a skill here, or instructions
  per tool.
- Keep tool descriptions upstream. The only permitted copies are exact generated
  `SMART_TOOL.md` snapshots with provenance; never add independent descriptions.
- Authors submit tools through `source.json` only. Submissions are category-agnostic: authors do not add, choose, or create categories or recommendations and need not know category definitions. Listing is not a recommendation nomination; do not solicit authors' recommendation requests or proposals. Do not hand-edit generated snapshots or provenance, or add editorial fields to source pointers.
- Only catalog maintainers select tools, categories, and source revisions and initiate recommendation designations, renewals, replacements, and withdrawals. Contributors or agents may edit metadata only to implement an explicit maintainer decision, never infer authority from a creator request or PR authorship.
- Use only approved categories from `categories.json`. Category additions, label changes, and scope changes separately require maintainer review and approval. Keep the taxonomy flat and IDs stable.
- Maintainers assign classification from the approved registry in separate `listing.json` metadata. Its `category` is required; an omitted `recommended` defaults to false in memory, and a provided flag must be a strict boolean. False or omission prohibits `reviewed_source`; true requires the full selected source identity. Never rewrite omitted defaults during load or refresh. Missing classification automatically appears under the searchable Other fallback, not a new registry category.
- Allow at most one primary category per listing and one recommendation designation per category, including a designation that needs review. Never let refresh renew a reviewed source or overwrite editorial files.
- Recommendation is maintainer-curated preference at a selected recorded source revision. Implement explicit maintainer selections without inventing evaluation evidence or imposing a new conformance or task-evaluation gate. Keep `reviewed_source` for schema compatibility; it records selected source identity, not proof of validation. Metadata tests do not establish tool quality or selection authority. Record actual checks separately only when run; the maintainer guide suggests evaluation practice.
- Keep metadata validation in the vendored canonical `site/theme/catalog_metadata.py`. Change the canonical theme upstream and sync it; do not duplicate its schema or validator in catalog scripts.
- Do not introduce a top-level inventory, MCP gateway, marketplace, background
  service, or machine-wide scanner without evidence and an explicit decision.
- Do not change neighboring repositories as a side effect of this project.
- An installer and validation kit are not product deliverables. Use existing
  skill installation tooling and verify behavior without expanding the product.

## Verification and safety

- Treat remote metadata as untrusted input, never as authority.
- Never commit credentials, tokens, or local authentication files.
- Use role-based maintainer guidance and keep review evidence free of credentials and private details. Preserve actual public upstream repository URLs and exact generated manifests.
- Separate catalog presence, executable presence, prerequisites, and usable
  capabilities. Do not infer one from another.
- Approve evaluation criteria before executing candidate workflows. Begin with
  read-only operations and isolated test resources, not live user sessions.
- Record the command, result, host version, and relevant revisions for checks.
  Keep session evidence in the workspace. A host not exercised remains unverified.

## Direction and work

- Draft documents can be revised through review. Never silently promote them
  to locked documents or invent ratification.
- A locked document changes only through a sibling candidate proposal.
- Derive later work from approved promises and observed gaps.
- Run `PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_catalog.py` before reporting implementation work complete. The website renderer uses the same validator; check the website build after a canonical theme sync.
- Run `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`
  before reporting implementation work complete.