# Maintainer curation

This guide is normative for catalog recommendation decisions. Ordinary listing contributions follow [Contributing](../README.md#contributing); they are not recommendation nominations.

Submissions are source-only and category-agnostic. Submitters do not add, choose, or create categories or recommendations and need not know category definitions. Maintainers assign classification from the approved registry in separate `listing.json` metadata, never in upstream manifests or source pointers.

## Roles and selection

Only catalog maintainers select the tool, primary category, and source revision and initiate designations, renewals, replacements, and withdrawals. Maintainers select, initiate, and promote; they are not merely approvers of creators' promotion requests. Contributors or agents may edit recommendation metadata only to implement an explicit maintainer decision, not make the selection. A creator request or PR authorship cannot authorize a recommendation.

Before merging a designation, renewal, or replacement, record the selection decision, category, and exact selected source identity in the pull request or repository maintainer notes. Recommendation means maintainer-curated preference at a selected recorded source revision. Implement an explicit maintainer selection without imposing a new conformance or task-evaluation gate. Do not claim that selection proves validation or that anyone completed a review.

Keep the metadata field name `reviewed_source` for schema compatibility: it records selected source identity, not proof of conformance or task results. A matching source identity or passing catalog tests establishes source binding and structure, not tool quality.

Digital Twin Universe is selected for Test environments at `a4915ad2ce0846ea4221fb264e2557aa2463d1ed`; Smart Tool Creator is selected for Smart Tool development at `a101e6f17ef86135393d105919d00522fcf59c55`. Both have `recommended: true` at those recorded identities. These are selections, not claims of completed conformance review or representative-task evaluation.

## Evaluation practice

Maintainers may review stability, conformance against the applicable Smart Tool specification, and useful outcomes through representative task scenarios for the selected category. These are suggested evaluation practices, distinct from source binding and not prerequisites to implementing an explicit maintainer selection. Record actual checks separately only when run; do not add duplicate evidence fields to `listing.json`. For checks that are run, record:

- Exact tool repository, distribution path, and full commit, plus the actual specification and evaluation revisions used.
- Criteria, commands, and results: **PASS** for observed success; **SKIP** with a reason for an unexercised or inapplicable check. Record failures and blockers honestly; a SKIP is not a pass.
- Representative task scenarios, the environment and host versions, provider and model setup where relevant (never credentials), and the inputs used.
- Expected outcomes and observed outcomes with evidence for each scenario.
- Scope and limitations, including skipped checks, unavailable providers or platforms, and capabilities not exercised.

Agree evaluation criteria before executing candidate workflows. Start with read-only operations and isolated resources; do not mutate live user sessions or infer permission to spend or access secrets from a listing. Missing evaluation evidence means validation has not been demonstrated, not that a selection is forbidden or a tool failed. Never invent evaluation models, results, or review confirmation.

Catalog metadata validation and rendering tests check structure, classification, source identity, and drift behavior. They do not evaluate tool quality, prove completed evaluation, or establish selection authority. “Recommended” is revision-scoped editorial judgment, not certification, guaranteed results, or proof of local installation, prerequisites, provider setup, or readiness.

## Categories

`categories.json` is a flat taxonomy of stable IDs, labels, and scopes. Category
additions, label changes, and scope changes require separate maintainer review
and approval before merge. Keep IDs stable when labels change; do not invent a
tool-specific category to evade the recommendation limit.

Each classified listing has at most one primary category. At most one
`recommended: true` designation may occupy a category, including a designation
that needs review. Missing listing metadata keeps entries available under Other and not recommended. Other is a built-in fallback grouping, not a registry category. Tools without classification automatically appear there and remain searchable by Name and Category; its filter option and group appear only when such entries exist. Without a registry, legacy rendering remains unchanged.

The ordinary metadata form is `{"category": "test-environments"}`. `category` is required and unknown registry IDs are rejected. An omitted `recommended` defaults to false in memory without rewriting the file. A provided flag must be a strict boolean; true requires the full selected `reviewed_source`, while false or omission prohibits it. Neither false nor omission occupies a recommendation slot.

## Metadata procedures

- Designate only after maintainers select the tool, category, and revision and initiate the designation; record `recommended: true` and the exact `reviewed_source`.
- Renew only after maintainers select the revision and initiate renewal; update `reviewed_source` to its exact repository, distribution path, and full commit. Never advance the selected commit automatically.
- Withdraw only after maintainers initiate withdrawal; remove `recommended` and `reviewed_source` to leave the category-only ordinary form. An explicit false flag is also valid. Keep the ordinary classified listing unless its removal is separately justified. Record the decision and rationale.
- Replace only after maintainers select the replacement and initiate replacement; withdraw the old designation and add the new one in the same change. The one-designation-per-category limit still applies.

`reviewed_source` is selected source identity metadata, neither an installer nor certification.
Effective recommendation requires agreement with the source pointer and
snapshot provenance on repository, distribution path, and commit. Drift keeps
the listing, category, and designation, but displays “Recommendation needs
review” and removes recommendation preference. The stale designation still
occupies its category's slot.

Automatic refresh must preserve `categories.json`, listings, and reviewed
commits byte for byte. Do not hand-edit generated manifests or provenance to
make identities agree; renewal is a deliberate maintainer selection.

## Evidence and enforcement

Keep review evidence free of credentials and private details. Preserve public
source URLs and exact generated snapshots.

Structural validation is not an authorization engine. Maintainer selection is a curation policy, not a claim of automated GitHub enforcement or completed evaluation.