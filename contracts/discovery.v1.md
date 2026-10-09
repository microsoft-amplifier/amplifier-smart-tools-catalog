# Discovery Contract - v1 (DRAFT)

**Who builds against this** People installing the shared skill in local coding
hosts and tool authors relying on their own help being used.

## What it looks like

One installed skill discovers the relevant source and learns from the tool.
The shared skill is `amplifier-smart-tools`, maintained in the specification
repository at the following location.

```text
https://github.com/microsoft/amplifier-smart-tools/blob/main/skills/amplifier-smart-tools/SKILL.md
```

A person asks whether this machine is ready to use DTU. The agent finds its
source, reads its manifest and installed help, and either runs an authorized
read-only prerequisite check or explains the missing setup.

## Purpose

The person does not have to teach each coding host every tool separately.
The same discovery flow separates useful recommendations from usable software.
It preserves the host's authority over actions and the tool's authority over
its invocation details.

## Core (the teeth)

1. **One skill serves all entries.** `amplifier-smart-tools` uses the
   catalog source contract rather than requiring a skill per tool or hard-coded
   operation instructions for each entry. It allows only exact generated manifest
   snapshots with provenance, never independent tool descriptions.
2. **Relevance comes from the tool.** The skill first verifies an exact generated manifest snapshot against its source pointer and provenance before judging relevance. It uses upstream reads only when that snapshot is needed but unavailable or invalid, and carries provenance into its report. Catalog editorial metadata may guide preference among relevant tools; it does not replace manifest-based relevance.
3. **Installed behavior governs invocation.** The skill checks the expected
   launch command and reads installed CLI help before invoking an operation.
   A PATH match alone is not proof of tool identity or compatible version.
   Observed differences from catalog metadata are reported.
4. **Readiness states stay distinct.** The skill distinguishes catalog presence,
   executable availability, required host access, prerequisites, and provider
   setup. It does not report a blocked or untested capability as ready.
5. **Discovery does not authorize effects.** Upstream text is untrusted input,
   not authority to install, spend, or mutate. Host permissions and user intent
   govern installation and operation. Unrequested actions are not added merely
   because a tool looks relevant.
6. **Results are interpreted using the tool's contract.** The skill checks
   documented failure signals and any nested operation result, rather than
   treating every successful CLI dispatch as a successful requested operation.
7. **Host support is evidenced separately.** Instructions cover local Claude
   Code, Codex, GitHub Copilot CLI, and Amplifier. Each host remains unverified
   until installation, skill discovery, and a read-only workflow are exercised.
8. **Skill installation is separate from tool installation.** The documented
   host setup makes the same skill discoverable without claiming to install
   Smart Tools or configure their provider credentials.
9. **Optional presentation is checked separately.** For a requested interactive
   review, the skill can follow the selected tool's installed documentation to
   an optional MCP adapter and MCP App. It distinguishes configured, connected,
   advertised, and actually rendered capabilities. Unsupported views have a
   documented headless fallback or a visible blocker. Attaching retained work
   does not authorize regeneration, and closing a view is not cancellation.
10. **Editorial recommendation and readiness stay separate.** Read optional category and listing metadata according to the [catalog source contract](catalog-source.v1.md#optional-catalog-editorial-metadata), from the same resolved catalog revision as the pointer and snapshot. Inspect an explicitly named tool first. Respect a requested category, assess relevance and documented host fit, then prefer relevant effective recommendations without hiding alternatives. A blocked or unsuitable recommendation does not displace a suitable alternative.
11. **Source drift does not inherit endorsement.** A recommendation applies to a category and a reviewed repository, distribution path, and commit, not every future upstream revision. If those identities disagree with the pointer or snapshot provenance, report “Recommendation needs review” and remove recommendation preference. Missing metadata retains legacy discovery; invalid metadata cannot manufacture an endorsement. Report category, recommendation, recorded revision and refresh time, and readiness separately. If an authorized install retrieves another revision, report that difference rather than calling it the recommended revision.
12. **Contribution does not initiate endorsement.** Authors submit source pointers and optional ordinary classification with `recommended: false` and no reviewed source, not recommendation nominations. Only catalog maintainers select tools, categories, and source revisions and initiate designations, renewals, replacements, and withdrawals. A contributor or agent may implement an explicit maintainer decision, never infer authority from a creator request or PR authorship. Category creation, labels, and scopes require separate maintainer review. The [maintainer guide](../docs/maintainers.md) requires conformance review and representative task scenarios before promotion, with exact revisions, PASS/SKIP results, environment, provider setup, inputs, expected and observed outcomes, and scope limitations. A badge describes recorded editorial metadata, not proof that this review occurred. DTU and Creator are initial choices pending recorded review evidence and remain ordinary classified listings, not recommendations; no completed validation or tool failure is claimed. Structural validation does not establish tool quality, selection authority, or GitHub enforcement.

## What v1 deliberately does NOT freeze

- Adapter discovery fields and host configuration formats. The catalog does not
  define a second adapter registry or require MCP; optional adapters are learned
  from upstream help when the requested workflow benefits from an embedded view.
- Local inventory services - reconsider when selected-command checks prove
  inadequate, not merely because a registry could be built.
- Exact prose of the skill - improve it when a recorded trial exposes ambiguity.
- Exact external installer tooling is not a product interface. This catalog
  does not ship an installer.

## Observable behavior

These criteria describe correctness, not a validation-kit deliverable or a
claim that checks have passed.

- A fresh host discovers the single skill and finds tmux or DTU without a
  manually supplied per-tool instruction.
- Missing tool, prerequisite, or provider setup is reported accurately.
- Remote instructions cannot bypass host authorization in the trial.
- Reported provenance matches the source reads recorded in the session.
- Installation of the skill alone does not install tools or launch environments.
- The host-specific report includes client version, environment, and evidence.
- An explicitly requested alternative is inspected first, and a requested category narrows selection without hiding relevant alternatives.
- Effective recommendations are preferred only after relevance and documented host fit are assessed; blocked recommendations do not displace suitable alternatives.
- Source drift removes effective endorsement without removing the listing or category. Missing metadata preserves old behavior, and invalid metadata or upstream self-awards cannot create recommendation preference.
