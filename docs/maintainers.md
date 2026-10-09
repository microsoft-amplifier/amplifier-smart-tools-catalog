# Maintainer curation

This guide is normative for catalog recommendation decisions. Ordinary listing
contributions follow [Contributing](../README.md#contributing); they are not
recommendation nominations.

## Roles and merge gate

Only catalog maintainers select the tool, primary category, and source revision
and initiate designations, renewals, replacements, and withdrawals. Maintainers
select, initiate, and promote; they are not merely approvers of creators'
promotion requests. Contributors or agents may edit recommendation metadata only
to implement an explicit maintainer decision, not make the selection. A creator
request or PR authorship cannot authorize a recommendation.

Before merging a designation, renewal, or replacement, maintainers must explicitly
record the review status, selection decision, rationale, and evidence in the
pull request or repository maintainer notes. Link the review evidence in that
record; do not add duplicate evidence fields to `listing.json`. Missing evidence
means pending review, not a completed review. Do not invent results or confirmation.

Complete and record the required review before setting `recommended: true` for
publication. A matching source identity or passing catalog tests is not a
substitute for that review.

Digital Twin Universe and Smart Tool Creator are initial choices pending
recorded review evidence. Both remain ordinary classified listings with
`recommended: false` and no `reviewed_source`. This is not a tool-failure or
negative quality judgment. They must meet the required review standard before
promotion.

## Required review standard

Recommendation requires both a conformance review against the applicable Smart
Tool specification and representative task scenarios for the selected category.
Record:

- Exact tool repository, distribution path, and full commit, plus the exact
  specification and evaluation revisions used.
- Conformance criteria, commands, and results: **PASS** for observed conformance;
  **SKIP** with a reason for an unexercised or inapplicable check. Record failures
  and blockers honestly; a SKIP is not a pass.
- Representative task scenarios, the environment and host versions, provider
  and model setup where relevant (never credentials), and the inputs used.
- Expected outcomes and observed outcomes with evidence for each scenario.
- The review's scope and limitations, including skipped checks, unavailable
  providers or platforms, and capabilities not exercised.
- An explicit maintainer review status and decision explaining whether the
  evidence supports the recommendation within that scope.

Agree evaluation criteria before executing candidate workflows. Start with
read-only operations and isolated resources; do not mutate live user sessions
or infer permission to spend or access secrets from a listing. Skips or missing
coverage that prevent a supported decision leave the proposal pending review.

Catalog metadata validation and rendering tests check structure, classification,
source identity, and drift behavior. They do not evaluate tool quality, prove
that this review occurred, or establish selection authority. “Recommended” is
revision-scoped editorial judgment, not certification, guaranteed results, or
proof of local installation, prerequisites, provider setup, or readiness.

## Categories

`categories.json` is a flat taxonomy of stable IDs, labels, and scopes. Category
additions, label changes, and scope changes require separate maintainer review
and approval before merge. Keep IDs stable when labels change; do not invent a
tool-specific category to evade the recommendation limit.

Each classified listing has at most one primary category. At most one
`recommended: true` designation may occupy a category, including a designation
that needs review. Missing listing metadata keeps legacy entries available,
not yet classified, and not recommended.

## Metadata procedures

- Designate only after maintainers select the tool, category, and reviewed
  revision, initiate the designation, and complete the required review; record
  `recommended: true` and the exact `reviewed_source`.
- Renew only after maintainers select and review the revision and initiate
  renewal; update `reviewed_source` to its exact repository, distribution path,
  and full commit. Never advance the reviewed commit automatically.
- Withdraw only after maintainers initiate withdrawal; set `recommended` to
  false and remove `reviewed_source`. Keep the ordinary classified listing
  unless its removal is separately justified. Record the decision and rationale.
- Replace only after maintainers select and review the replacement and initiate
  replacement; withdraw the old designation and add the new one in the same
  change. The one-designation-per-category limit still applies.

`reviewed_source` is identity metadata, neither an installer nor certification.
Effective recommendation requires agreement with the source pointer and
snapshot provenance on repository, distribution path, and commit. Drift keeps
the listing, category, and designation, but displays “Recommendation needs
review” and removes recommendation preference. The stale designation still
occupies its category's slot.

Automatic refresh must preserve `categories.json`, listings, and reviewed
commits byte for byte. Do not hand-edit generated manifests or provenance to
make identities agree; renewal is a deliberate reviewed decision.

## Evidence and enforcement

Keep review evidence free of credentials and private details. Preserve public
source URLs and exact generated snapshots.

Structural validation is not an authorization engine. Maintainer review is a
merge gate, not a claim of automated GitHub enforcement.