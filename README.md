# Amplifier Smart Tools Catalog

A catalog of [Amplifier Smart Tools](https://github.com/microsoft/amplifier-smart-tools).
Browse [the catalog](tools/) or the [website](https://microsoft.github.io/amplifier-smart-tools-catalog/).

## Use the catalog from your agent

Install the [Amplifier Smart Tools skill](https://github.com/microsoft/amplifier-smart-tools/blob/main/skills/amplifier-smart-tools/SKILL.md).
It reads this catalog to find and install tools, drives them through their own
help, and covers creating a tool and adding it here.

```bash
npx skills add microsoft/amplifier-smart-tools
```

Then ask your agent for a Smart Tool for the task. The skill normally reads the
catalog from GitHub; to use a local checkout instead, give your agent that path.
Adding the skill does not install Smart Tools or configure credentials.

## Catalog details

<details>
<summary>How source pointers and automatic refresh work</summary>

Each `tools/<slug>/source.json` points to an upstream repository. Optional `ref`
selects a branch, tag, or commit and defaults to `main`. Optional `path` selects
the tool's distribution root and defaults to the repository root.

The refresh action generates exact `SMART_TOOL.md` snapshots and provenance
after source changes reach `main`, daily, and on manual dispatch. Changes to
the refresh implementation also trigger it.

Tools own their manifests and usage help. The skill reads the snapshots first
and follows upstream guidance when needed. A recorded refresh time says when
the last refresh succeeded, not that the snapshot is currently fresh. Failed
source refreshes preserve the previous snapshot and appear in the action logs.

</details>

### Domains and recommendations

The catalog owns the approved work domains in [`domains.json`](domains.json). Optional `tools/<slug>/listing.json` files classify an entry and record a recommendation for a reviewed source revision. Missing listing metadata means listed, not yet classified, and not recommended. Ordinary listings remain available; they are not rejected or unapproved.

| Domain | Scope | Recommended tool |
|---|---|---|
| Test environments | Create and operate isolated environments for testing software and reproducing failures. | Digital Twin Universe |
| Smart Tool development | Create, extend, check, and evaluate Smart Tools. | Smart Tool Creator |

“Recommended” is a catalog editorial decision, not certification, proof of professional-quality outcomes, or a claim that the tool is installed or ready on this machine. It does not authorize installation, execution, spending, or access to secrets. The tool's own manifest still determines whether it fits the request.

A recommendation is effective only when its reviewed repository, distribution path, and commit agree with the source pointer and snapshot provenance. When they no longer agree, the entry keeps its domain and designation but shows “Recommendation needs review” instead of an effective recommendation. It loses recommendation preference until maintainers review it again. A stale designation still occupies the domain's one recommendation slot. Refresh time and recorded revision are evidence of a past snapshot, not current tool health.

## Product direction

- [Vision](docs/VISION.md)
- [Catalog source contract](contracts/catalog-source.v1.md)
- [Discovery contract](contracts/discovery.v1.md)

## Contributing

To propose a tool, add or update `tools/<slug>/source.json`. You may also propose optional `tools/<slug>/listing.json` classification using an existing approved domain and `"recommended": false`. Do not hand-copy or hand-edit generated `SMART_TOOL.md` or `provenance.json` files. After a source pointer merges to `main`, the refresh workflow generates snapshots and provenance. Never add classification or recommendation fields to `source.json` or upstream manifests.

### Editorial approval

Changes to domains or recommendations require review and approval from the designated approver, Brian or Sam, before merging. Name that approver in the pull request and describe the domain, source identity, and reason for the decision. Tool authors may propose an entry or classification; upstream content cannot award itself the catalog's recommendation.

- Propose a new domain by changing `domains.json` through review. A listing cannot invent a private domain to bypass the limit. Keep identifiers stable when labels change; changes to scope require editorial approval.
- Renew a recommendation by reviewing the selected source revision and updating `reviewed_source` to its exact repository, distribution path, and full commit. Do not move the reviewed commit automatically or fabricate evaluation evidence.
- Withdraw a recommendation by setting `recommended` to false and removing its reviewed source. Keep the ordinary classified listing unless its removal is separately justified.
- Replace a recommendation by withdrawing the old designation and adding the new one in the same change. There may be at most one `recommended: true` designation per domain, including ones that need review.

[Brian's public account](https://github.com/bkrabach) is identified in the [catalog's public contributor records](https://api.github.com/repos/microsoft/amplifier-smart-tools-catalog/contributors). Sam's reviewer account and the required repository permissions, code-owner review rules, and branch protection have not been verified. This approval policy is not a claim of GitHub enforcement. Maintainers must verify the reviewer accounts and protection settings before relying on automated enforcement; do not guess a `CODEOWNERS` identity or change repository settings as part of a listing contribution.

### Check a contribution

Use Python 3.12 or later with `site/requirements.txt` installed in your workspace virtual environment, as in the [site build instructions](site/README.md#build-and-preview). The full tests exercise snapshot rendering and require PyYAML. From the repository root, with that environment active:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_catalog.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The CLI and website build use the same validator in the versioned canonical theme. Do not add a separate schema or a second implementation here. Metadata validation does not evaluate tool quality or prove the approval policy has been enforced.

### Review a website preview

The Website workflow uploads a `github-pages` artifact for relevant pull requests, retained for seven days. Pull requests do not deploy. Open the exact Website run for the pull request and confirm its revision before downloading its artifact; do not choose the latest run by accident.

With GitHub CLI installed, replace the run ID below with that exact run. Choose a temporary directory under a preview parent you control; this example keeps it in the checkout's ignored `.work/` directory.

```sh
RUN_ID='<exact Website run ID>'
PREVIEW_PARENT="$PWD/.work"
mkdir -p "$PREVIEW_PARENT"
PREVIEW_DIR="$(mktemp -d "$PREVIEW_PARENT/catalog-preview.XXXXXX")"
gh run download "$RUN_ID" --repo microsoft/amplifier-smart-tools-catalog --name github-pages --dir "$PREVIEW_DIR/download"
mkdir "$PREVIEW_DIR/site"
tar -xf "$PREVIEW_DIR/download/artifact.tar" -C "$PREVIEW_DIR/site"
PYTHONDONTWRITEBYTECODE=1 python3 -m http.server 8000 --bind 127.0.0.1 --directory "$PREVIEW_DIR/site"
```

`gh run download` extracts the artifact's outer ZIP into `download/`; the remaining `artifact.tar` contains the site files directly, so no extra `_site/` prefix is needed when serving `site/`.

Open `http://127.0.0.1:8000` to inspect the static build. That address is only a local serving address, not source provenance or a public deployment. The source revision is the one shown on the selected GitHub run. The Actions UI also offers the same `github-pages` download as a ZIP containing `artifact.tar`; extract the ZIP into the chosen download directory before using the tar command.

After either a successful or failed trusted main refresh, the Website workflow rebuilds validated current `main`. A refresh may have committed successful entries before reporting another entry's failure, so a failure must not leave an outdated recommendation badge published. The workflow ignores triggering-run artifacts and never deploys untrusted pull-request content. Manual publication is restricted to `main`; other revisions are preview-only.

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (for example, with
a status check or comment). Simply follow the instructions provided by the bot.
You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](CODE_OF_CONDUCT.md).
For more information, see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/)
or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with questions
or comments. See [SECURITY.md](SECURITY.md) to report vulnerabilities.

## Trademarks

This project may contain trademarks or logos for projects, products, or
services. Authorized use of Microsoft trademarks or logos is subject to and
must follow [Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must
not cause confusion or imply Microsoft sponsorship. Any use of third-party
trademarks or logos is subject to those third-party's policies.

## License

[MIT](LICENSE)
