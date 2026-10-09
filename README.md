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

### Categories and recommendations

The catalog owns a flat category registry in [`categories.json`](categories.json), with stable IDs, labels, and scopes. Optional `tools/<slug>/listing.json` files assign at most one primary category and record a recommendation for a reviewed source revision. Missing listing metadata means listed, not yet classified, and not recommended. Ordinary listings remain available; they are not rejected or unapproved.

This change proposes seven additional categories and ordinary classifications based on the work described in the exact, commit-pinned public manifests, not repository names. The two existing category labels and scopes are unchanged. The additions and assignments require maintainer review before merge; this proposal does not claim that approval has occurred.

All 22 current tools are classified across these nine categories: zero are unclassified and zero are Recommended. Classification is not a completed recommendation evaluation. Future source-pointer contributions may still omit classification while their category is considered.

| Category | Tools | Current listings |
|---|---:|---|
| Test environments | 1 | `digital-twin-universe` |
| Smart Tool development | 1 | `smart-tool-creator` |
| Research & knowledge | 5 | `deep-research`, `fact-check`, `hacker-news`, `lore`, `team-pulse` |
| Audio, video & animation | 5 | `aud`, `vid`, `outtake`, `unfold`, `showrun` |
| Presentations & documents | 1 | `stories` |
| App design & developer tools | 4 | `possibly`, `fast-decisions`, `github-repos`, `tmux` |
| Email, calendar & work preparation | 2 | `gmail`, `workiq` |
| Music & playlists | 2 | `music-deck`, `spotify` |
| Smart home | 1 | `home-assistant` |

Digital Twin Universe and Smart Tool Creator are initial choices pending recorded review evidence. Both remain ordinary classified listings with `recommended: false` and no `reviewed_source`; no completed review or approval is claimed. This records missing review evidence, not a tool failure or negative quality judgment. Maintainers must agree evaluation criteria, select the tool and revision, and complete the [required review standard](docs/maintainers.md#required-review-standard) before promotion.

“Recommended” means catalog maintainers selected a tool for a category at an exact reviewed source revision after the required conformance review and representative task scenarios. It is not certification, a guarantee of outcomes, or a claim that the tool is installed or ready on this machine. It does not authorize installation, execution, spending, or access to secrets. The tool's own manifest still determines whether it fits the request. Catalog metadata tests check structure and source identity, not tool quality or completion of that review.

A recommendation is effective only when its reviewed repository, distribution path, and commit agree with the source pointer and snapshot provenance. `reviewed_source` is source identity metadata, neither an installer nor certification. When identities no longer agree, the entry keeps its category and designation but shows “Recommendation needs review” instead of an effective recommendation. It loses recommendation preference until maintainers review a revision and explicitly initiate renewal. A stale designation still occupies the category's one recommendation slot. Refresh time and recorded revision are evidence of a past snapshot, not current tool health. A badge describes recorded editorial metadata, not proof that the maintainer review gate was completed.

The website explains Recommended and offers a “Recommended only” checkbox. It narrows results to effective recommendations alongside search, platform, and primary category filters; it excludes designations that need review. Leave it unchecked to see ordinary and not-yet-classified listings too.

## Product direction

- [Vision](docs/VISION.md)
- [Catalog source contract](contracts/catalog-source.v1.md)
- [Discovery contract](contracts/discovery.v1.md)

## Maintainer curation

Only catalog maintainers select and initiate recommendations and promote tools after review. Complete and record the required review before setting `recommended: true` for publication. Curation is separate from ordinary listing contributions; the normative roles, required evidence, category review, and metadata procedures live in the [maintainer guide](docs/maintainers.md).

## Contributing

1. Add or update `tools/<slug>/source.json` to point to the tool's public upstream distribution.
2. You may also submit optional `tools/<slug>/listing.json` classification using an existing approved category and `"recommended": false`, with no reviewed source.
3. Run the [contribution checks](#check-a-contribution) and submit a pull request.

Listing or contributing a tool is not a recommendation nomination. Do not solicit recommendation requests or proposals from authors. Do not hand-copy or hand-edit generated `SMART_TOOL.md` or `provenance.json` files. After a source pointer merges to `main`, the refresh workflow generates snapshots and provenance. Never add classification or recommendation fields to `source.json` or upstream manifests.

### Check a contribution

Use Python 3.12 or later with `site/requirements.txt` installed in your workspace virtual environment, as in the [site build instructions](site/README.md#build-and-preview). The full tests exercise snapshot rendering and require PyYAML. From the repository root, with that environment active:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_catalog.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The CLI and website build use the same validator in the versioned canonical theme. Do not add a separate schema or a second implementation here. Metadata validation does not evaluate tool quality or prove the selection and initiation policy has been enforced.

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
