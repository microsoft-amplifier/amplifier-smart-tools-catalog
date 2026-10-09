"""Unit tests for scripts/refresh_manifests.py; they do not contact upstreams."""

from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "refresh_manifests.py"
SPEC = importlib.util.spec_from_file_location("refresh_manifests", SCRIPT)
assert SPEC and SPEC.loader
refresh_manifests = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = refresh_manifests
SPEC.loader.exec_module(refresh_manifests)


class RefreshManifestsTests(unittest.TestCase):
    def test_catalog_points_at_the_shared_skill_and_ships_none_of_its_own(self) -> None:
        catalog_root = SCRIPT.parents[1]
        readme = (catalog_root / "README.md").read_text()

        self.assertIn("npx skills add microsoft/amplifier-smart-tools\n", readme)
        self.assertIn(
            "https://github.com/microsoft/amplifier-smart-tools/blob/main/skills/amplifier-smart-tools/SKILL.md",
            readme,
        )
        for removed in ("skills", "behaviors", "bundle.md"):
            self.assertFalse((catalog_root / removed).exists(), removed)

    def test_repository_readiness_files_describe_the_minimal_contribution_flow(self) -> None:
        catalog_root = SCRIPT.parents[1]
        readme = (catalog_root / "README.md").read_text()
        support = (catalog_root / "SUPPORT.md").read_text()
        workflow = (catalog_root / ".github" / "workflows" / "ci.yml").read_text()

        self.assertIn("optional `tools/<slug>/listing.json`", readme)
        self.assertIn('"recommended": false`, with no reviewed source', readme)
        self.assertIn("Listing or contributing a tool is not a recommendation nomination.", readme)
        self.assertIn("Do not solicit recommendation requests or proposals from authors.", readme)
        self.assertIn("[maintainer guide](docs/maintainers.md)", readme)
        self.assertIn("Only catalog maintainers select and initiate recommendations", readme)
        self.assertIn(
            "Complete and record the required review before setting `recommended: true` for publication.",
            readme,
        )
        self.assertIn("initial choices pending recorded review evidence", readme)
        self.assertIn("Both remain ordinary classified listings", readme)
        self.assertIn("not a tool failure or negative quality judgment", readme)
        self.assertIn("no completed review or approval is claimed", readme)
        self.assertIn("not certification", readme)
        self.assertNotIn("source pointers only", readme)
        self.assertIn("generated `SMART_TOOL.md`", readme)
        self.assertIn("[Microsoft Open Source Code of Conduct](CODE_OF_CONDUCT.md)", readme)
        self.assertIn("[SECURITY.md](SECURITY.md)", readme)
        self.assertIn("Contributor License Agreement (CLA)", readme)
        self.assertIn("Microsoft's Trademark & Brand Guidelines", readme)
        self.assertEqual(
            support,
            """# Support

For catalog issues, open an issue in this repository. For individual Smart Tool
behavior, contact the upstream repository identified by that tool's source
pointer.

Do not report security vulnerabilities publicly; follow [SECURITY.md](SECURITY.md).

This repository does not make a response-time commitment.""",
        )
        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("branches: [main]", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("runs-on: ubuntu-latest", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("actions/setup-python@v5", workflow)
        self.assertIn("python3 -m pip install -r site/requirements.txt", workflow)
        self.assertIn("PYTHONDONTWRITEBYTECODE=1 python3 scripts/validate_catalog.py", workflow)
        self.assertIn("PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v", workflow)
        self.assertNotIn("refresh_manifests.py", workflow)

    def test_contributor_listing_steps_are_separate_from_maintainer_procedures(self) -> None:
        catalog_root = SCRIPT.parents[1]
        readme = (catalog_root / "README.md").read_text()
        contribution = readme.split("## Contributing\n", 1)[1].split("### Check a contribution", 1)[0]
        self.assertIn("1. Add or update `tools/<slug>/source.json`", contribution)
        self.assertIn("existing approved category", contribution)
        self.assertIn('"recommended": false`, with no reviewed source', contribution)
        self.assertNotIn("reviewed_source", contribution)
        self.assertNotIn("recommended: true", contribution)
        for action in ("Designate", "Renew", "Withdraw", "Replace"):
            self.assertNotIn(f"- {action} only after", readme)

    def test_maintainer_guide_requires_revision_scoped_review_evidence_before_merge(self) -> None:
        catalog_root = SCRIPT.parents[1]
        guide = re.sub(r"\s+", " ", (catalog_root / "docs" / "maintainers.md").read_text())
        self.assertIn("This guide is normative", guide)
        self.assertIn("Only catalog maintainers select the tool, primary category, and source revision", guide)
        self.assertIn("select, initiate, and promote", guide)
        self.assertIn("to implement an explicit maintainer decision, not make the selection", guide)
        self.assertIn("request or PR authorship cannot authorize a recommendation", guide)
        self.assertIn("Before merging a designation, renewal, or replacement", guide)
        self.assertIn("review status, selection decision, rationale, and evidence", guide)
        self.assertIn("pull request or repository maintainer notes", guide)
        self.assertIn("do not add duplicate evidence fields to `listing.json`", guide)
        self.assertIn(
            "Complete and record the required review before setting `recommended: true` for publication.",
            guide,
        )
        self.assertIn("Keep review evidence free of credentials and private details.", guide)
        for evidence in (
            "conformance review",
            "representative task scenarios",
            "Exact tool repository, distribution path, and full commit",
            "specification and evaluation revisions",
            "**PASS**",
            "**SKIP** with a reason",
            "environment and host versions",
            "provider and model setup",
            "inputs used",
            "Expected outcomes and observed outcomes",
            "scope and limitations",
            "Missing evidence means pending review",
            "They must meet the required review standard before promotion",
            "They do not evaluate tool quality",
            "Structural validation is not an authorization engine",
        ):
            self.assertIn(evidence, guide)
        for action in ("Designate", "Renew", "Withdraw", "Replace"):
            self.assertIn(f"- {action} only after maintainers", guide)
        self.assertIn("flat taxonomy of stable IDs, labels, and scopes", guide)
        self.assertIn("at most one primary category", guide)
        self.assertIn("including a designation that needs review", guide)
        self.assertIn("identity metadata, neither an installer nor certification", guide)
        self.assertIn("not certification, guaranteed results", guide)
        agents = (catalog_root / "AGENTS.md").read_text()
        self.assertIn("normative maintainer curation and review standard", agents)
        self.assertIn("`docs/maintainers.md`", agents)

    def test_public_guidance_uses_roles_without_account_approval_links(self) -> None:
        catalog_root = SCRIPT.parents[1]
        paths = ("README.md", "AGENTS.md", "docs/VISION.md", "docs/maintainers.md",
                 "contracts/catalog-source.v1.md", "contracts/discovery.v1.md", "site/README.md")
        for relative in paths:
            with self.subTest(file=relative):
                text = (catalog_root / relative).read_text()
                self.assertIn("maintainer", text.lower())
                # Public repository identities are legitimate source references;
                # profile links and account-identification policy are not.
                self.assertNotRegex(text, r"https://github\.com/[^/\s)]+(?:\)|\s|$)")
                self.assertNotRegex(text, r"https://api\.github\.com/repos/[^\s)]+/contributors")
                self.assertNotRegex(text, r"Only [A-Z][a-z]+ or [A-Z][a-z]+")

    def test_website_guidance_explains_effective_recommendations_and_filters(self) -> None:
        catalog_root = SCRIPT.parents[1]
        site = re.sub(r"\s+", " ", (catalog_root / "site" / "README.md").read_text())
        for phrase in (
            "flat `categories.json` taxonomy",
            "primary `category`",
            "conformance review and representative task scenarios",
            "exact reviewed source revision",
            "not certification, guaranteed outcomes, or proof of local readiness",
            "“Recommended only” checkbox",
            "unchecked by default",
            "combines with the other filters",
            "includes only effective recommendations",
            "designations do not qualify",
            "Clear filters resets it",
            "with JavaScript disabled, all tools remain visible",
        ):
            self.assertIn(phrase, site)

    def test_public_tool_sources_use_root_main_distributions(self) -> None:
        catalog_root = SCRIPT.parents[1]
        expected_repositories = {
            "home-assistant": "https://github.com/bkrabach/amplifier-smart-tool-home-assistant.git",
            "music-deck": "https://github.com/bkrabach/amplifier-smart-tool-music-deck.git",
        }

        for slug, repository in expected_repositories.items():
            source_file = catalog_root / "tools" / slug / "source.json"
            self.assertEqual(json.loads(source_file.read_text()), {"repository": repository})
            self.assertEqual(
                refresh_manifests.parse_source(source_file),
                refresh_manifests.Source(repository, "main", "."),
            )

    def test_parse_source_defaults_and_rejects_credential_url(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            source_file = Path(temporary_name) / "source.json"
            source_file.write_text('{"repository": "https://example.test/tool.git"}')
            self.assertEqual(
                refresh_manifests.parse_source(source_file),
                refresh_manifests.Source("https://example.test/tool.git", "main", "."),
            )

            source_file.write_text(
                '{"repository": "https://token@example.test/tool.git", "path": "../tool"}'
            )
            with self.assertRaises(refresh_manifests.RefreshError):
                refresh_manifests.parse_source(source_file)

    def test_prepare_snapshot_preserves_manifest_bytes_and_records_provenance(self) -> None:
        cache = Mock()
        cache.resolve.return_value = (Path("/temporary/source.git"), "a" * 40)
        cache.environment = {}
        cache.timeout = 1
        descriptor = b'{"manifest": "docs/SMART_TOOL.md"}\n'
        manifest = b"# Tool\r\n\nExact bytes.\x00\n"

        with (
            patch.object(refresh_manifests, "object_type", return_value="tree"),
            patch.object(
                refresh_manifests,
                "read_repository_file",
                side_effect=[descriptor, manifest],
            ),
        ):
            prepared = refresh_manifests.prepare_snapshot(
                refresh_manifests.Source("https://example.test/tool.git", "main", "tool"),
                cache,
            )

        self.assertEqual(prepared.manifest, manifest)
        provenance = json.loads(prepared.provenance)
        self.assertEqual(
            provenance["source"],
            {
                "repository": "https://example.test/tool.git",
                "ref": "main",
                "path": "tool",
                "commit": "a" * 40,
            },
        )
        self.assertEqual(provenance["original_manifest_path"], "tool/docs/SMART_TOOL.md")
        self.assertTrue(provenance["last_success"].endswith("Z"))

    def test_prepare_snapshot_rejects_invalid_manifest_location_or_content(self) -> None:
        cache = Mock()
        cache.resolve.return_value = (Path("/temporary/source.git"), "a" * 40)

        with (
            patch.object(refresh_manifests, "object_type", return_value="tree"),
            patch.object(
                refresh_manifests,
                "read_repository_file",
                return_value=b'{"manifest": "notes.md"}',
            ),
        ):
            with self.assertRaisesRegex(refresh_manifests.RefreshError, "SMART_TOOL.md"):
                refresh_manifests.prepare_snapshot(
                    refresh_manifests.Source("https://example.test/tool.git", "main", "tool"),
                    cache,
                )

        with (
            patch.object(refresh_manifests, "object_type", return_value="tree"),
            patch.object(
                refresh_manifests,
                "read_repository_file",
                side_effect=[b'{"manifest": "SMART_TOOL.md"}', b""],
            ),
        ):
            with self.assertRaisesRegex(refresh_manifests.RefreshError, "nonempty"):
                refresh_manifests.prepare_snapshot(
                    refresh_manifests.Source("https://example.test/tool.git", "main", "tool"),
                    cache,
                )

    def test_refresh_keeps_existing_pair_when_preparation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            root = Path(temporary_name)
            entry = root / "tools" / "tool"
            entry.mkdir(parents=True)
            (entry / "source.json").write_text('{"repository": "https://example.test/tool.git"}')
            (entry / "SMART_TOOL.md").write_bytes(b"old manifest")
            (entry / "provenance.json").write_bytes(b'{"old": true}\n')
            listing = b'{ "category": "test-environments", "recommended": true }\r\n'
            categories = b'{ "categories": [] }\r\n'
            (entry / "listing.json").write_bytes(listing)
            (root / "categories.json").write_bytes(categories)
            errors = io.StringIO()

            with (
                patch.object(
                    refresh_manifests,
                    "prepare_snapshot",
                    side_effect=refresh_manifests.RefreshError("requested ref fetch failed"),
                ),
                redirect_stderr(errors),
            ):
                status = refresh_manifests.refresh(root, 1)

            self.assertEqual(status, 1)
            self.assertEqual((entry / "SMART_TOOL.md").read_bytes(), b"old manifest")
            self.assertEqual((entry / "provenance.json").read_bytes(), b'{"old": true}\n')
            self.assertEqual((entry / "listing.json").read_bytes(), listing)
            self.assertEqual((root / "categories.json").read_bytes(), categories)
            self.assertIn("ERROR tool: requested ref fetch failed", errors.getvalue())

    def test_successful_refresh_preserves_editorial_files_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            root = Path(temporary_name)
            entry = root / "tools" / "tool"
            entry.mkdir(parents=True)
            pointer = b'{"repository": "https://example.test/tool.git"}\n'
            listing = (
                b'{ "category": "test-environments", "recommended": true, '
                b'"reviewed_source": {"repository": "https://example.test/tool.git", '
                b'"path": ".", "commit": "' + b"a" * 40 + b'"} }\r\n'
            )
            categories = b'{ "categories": [{"id":"test-environments","label":"Tests","scope":"Testing."}] }\r\n'
            (entry / "source.json").write_bytes(pointer)
            (entry / "listing.json").write_bytes(listing)
            (root / "categories.json").write_bytes(categories)
            prepared = refresh_manifests.PreparedSnapshot(
                b"new manifest\n",
                json.dumps({"source": {"commit": "b" * 40}}).encode(),
            )

            with (
                patch.object(refresh_manifests, "prepare_snapshot", return_value=prepared),
                redirect_stdout(io.StringIO()),
            ):
                status = refresh_manifests.refresh(root, 1)

            self.assertEqual(status, 0)
            self.assertEqual((entry / "SMART_TOOL.md").read_bytes(), prepared.manifest)
            self.assertEqual((entry / "provenance.json").read_bytes(), prepared.provenance)
            self.assertEqual((entry / "source.json").read_bytes(), pointer)
            self.assertEqual((entry / "listing.json").read_bytes(), listing)
            self.assertEqual((root / "categories.json").read_bytes(), categories)

    def test_partial_refresh_preserves_editorial_files_for_all_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            root = Path(temporary_name)
            categories = b'{ "categories": [] }\r\n'
            (root / "categories.json").write_bytes(categories)
            listing = b'{ "category": "test-environments", "recommended": false }\r\n'
            for slug in ("first", "second"):
                entry = root / "tools" / slug
                entry.mkdir(parents=True)
                (entry / "source.json").write_text('{"repository": "https://example.test/tool.git"}')
                (entry / "listing.json").write_bytes(listing)
                (entry / "SMART_TOOL.md").write_bytes(b"old manifest")
                (entry / "provenance.json").write_bytes(b"old provenance")
            prepared = refresh_manifests.PreparedSnapshot(b"new manifest", b"new provenance")

            with (
                patch.object(
                    refresh_manifests,
                    "prepare_snapshot",
                    side_effect=[prepared, refresh_manifests.RefreshError("fetch failed")],
                ),
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                status = refresh_manifests.refresh(root, 1)

            self.assertEqual(status, 1)
            self.assertEqual((root / "categories.json").read_bytes(), categories)
            for slug in ("first", "second"):
                self.assertEqual((root / "tools" / slug / "listing.json").read_bytes(), listing)
            self.assertEqual((root / "tools" / "first" / "SMART_TOOL.md").read_bytes(), prepared.manifest)
            self.assertEqual((root / "tools" / "first" / "provenance.json").read_bytes(), prepared.provenance)
            self.assertEqual((root / "tools" / "second" / "SMART_TOOL.md").read_bytes(), b"old manifest")
            self.assertEqual((root / "tools" / "second" / "provenance.json").read_bytes(), b"old provenance")

    def test_refresh_returns_fatal_code_for_snapshot_output_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            root = Path(temporary_name)
            entry = root / "tools" / "tool"
            entry.mkdir(parents=True)
            (entry / "source.json").write_text('{"repository": "https://example.test/tool.git"}')
            listing = b'{ "category": "test-environments", "recommended": false }\r\n'
            categories = b'{ "categories": [] }\r\n'
            (entry / "listing.json").write_bytes(listing)
            (root / "categories.json").write_bytes(categories)
            errors = io.StringIO()

            with (
                patch.object(
                    refresh_manifests,
                    "prepare_snapshot",
                    return_value=refresh_manifests.PreparedSnapshot(b"manifest", b"provenance"),
                ),
                patch.object(
                    refresh_manifests,
                    "replace_pair",
                    side_effect=refresh_manifests.OutputError("snapshot output failed"),
                ),
                redirect_stderr(errors),
            ):
                status = refresh_manifests.refresh(root, 1)

            self.assertEqual(status, 2)
            self.assertEqual((entry / "listing.json").read_bytes(), listing)
            self.assertEqual((root / "categories.json").read_bytes(), categories)
            self.assertIn("FATAL tool: snapshot output failed", errors.getvalue())

    def test_cache_fetches_a_repository_ref_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_name:
            source = refresh_manifests.Source("https://example.test/tool.git", "main", ".")
            commit = b"b" * 40 + b"\n"
            with patch.object(
                refresh_manifests,
                "run_git",
                side_effect=[b"", b"", b"", commit],
            ) as run_git:
                cache = refresh_manifests.RepositoryCache(Path(temporary_name), 1)
                first = cache.resolve(source)
                second = cache.resolve(source)

            self.assertEqual(first, second)
            fetches = [
                call
                for call in run_git.call_args_list
                if call.args[0][:2] == ["fetch", "--no-tags"]
            ]
            self.assertEqual(len(fetches), 1)


if __name__ == "__main__":
    unittest.main()