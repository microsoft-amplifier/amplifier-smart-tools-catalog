"""Exercise the canonical validator against catalog fixtures and real seed data."""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site" / "theme"))
from catalog_metadata import (
    catalog_sources,
    load_catalog_metadata,
    read_json,
    read_snapshot,
    recommendation_state,
    validate_pointer,
)


DOMAIN = {"id": "test-environments", "label": "Test environments", "scope": "Isolated testing."}
IDENTITY = {"repository": "https://example.test/tool.git", "path": ".", "commit": "a" * 40}
LISTING = {"domain": DOMAIN["id"], "recommended": True, "reviewed_source": IDENTITY}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


class CatalogCards(HTMLParser):
    """Observe rendered card order, classification, and badges, not source code."""

    def __init__(self, document: str) -> None:
        super().__init__()
        self.cards: list[dict[str, object]] = []
        self.card: dict[str, object] | None = None
        self.feed(document)

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = dict(attributes)
        if tag == "article" and attrs.get("class") == "catalog-card":
            self.card = {"slug": attrs["data-tool"], "domain": attrs.get("data-domain"), "badges": []}
            self.cards.append(self.card)
        elif tag == "span" and self.card is not None:
            classes = (attrs.get("class") or "").split()
            if "recommendation" in classes:
                self.card["badges"].append(classes)

    def handle_endtag(self, tag: str) -> None:
        if tag == "article":
            self.card = None


def rendered_catalog(root: Path) -> str:
    spec = importlib.util.spec_from_file_location("catalog_theme_build", ROOT / "site" / "theme" / "build.py")
    assert spec and spec.loader
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    return renderer.catalog({}, SimpleNamespace(local=False, family_owner="microsoft"), root)


class CatalogMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        write_json(self.root / "domains.json", {"domains": [DOMAIN]})
        self.add_entry("tool", LISTING)

    def add_entry(self, slug: str, listing: object | None) -> Path:
        entry = self.root / "tools" / slug
        write_json(entry / "source.json", {"repository": IDENTITY["repository"]})
        write_json(
            entry / "provenance.json",
            {
                "source": {**IDENTITY, "ref": "main"},
                "original_manifest_path": "SMART_TOOL.md",
                "last_success": "2026-10-07T03:38:13Z",
            },
        )
        (entry / "SMART_TOOL.md").write_text(
            "---\nname: Tool\ndescription: A fixture tool.\nplatforms: [linux]\nuse_cases: [testing]\n---\n# Tool\n",
            encoding="utf-8",
        )
        if listing is not None:
            write_json(entry / "listing.json", listing)
        return entry

    def test_valid_recommendation_and_classified_alternative(self) -> None:
        self.add_entry("alternative", {"domain": DOMAIN["id"], "recommended": False})
        domains, listings = load_catalog_metadata(self.root)
        self.assertEqual(domains, {DOMAIN["id"]: DOMAIN})
        self.assertEqual(listings["tool"], LISTING)
        self.assertEqual(listings["alternative"], {"domain": DOMAIN["id"], "recommended": False})

    def test_missing_metadata_preserves_legacy_catalog(self) -> None:
        (self.root / "domains.json").unlink()
        (self.root / "tools" / "tool" / "listing.json").unlink()
        self.assertEqual(load_catalog_metadata(self.root), (None, {}))

    def test_registry_with_unclassified_listing_is_valid(self) -> None:
        self.add_entry("unclassified", None)
        domains, listings = load_catalog_metadata(self.root)
        self.assertEqual(domains, {DOMAIN["id"]: DOMAIN})
        self.assertNotIn("unclassified", listings)

    def test_new_pointer_does_not_require_a_generated_snapshot(self) -> None:
        entry = self.add_entry("new-tool", None)
        (entry / "SMART_TOOL.md").unlink()
        (entry / "provenance.json").unlink()
        _, listings = load_catalog_metadata(self.root)
        self.assertNotIn("new-tool", listings)

    def test_unknown_domain_and_listing_without_registry_fail(self) -> None:
        write_json(self.root / "tools" / "tool" / "listing.json", {**LISTING, "domain": "self-awarded"})
        with self.assertRaises(ValueError):
            load_catalog_metadata(self.root)
        write_json(self.root / "tools" / "tool" / "listing.json", LISTING)
        (self.root / "domains.json").unlink()
        with self.assertRaises(ValueError):
            load_catalog_metadata(self.root)

    def test_duplicate_domain_and_second_designation_fail(self) -> None:
        write_json(self.root / "domains.json", {"domains": [DOMAIN, DOMAIN]})
        with self.assertRaises(ValueError):
            load_catalog_metadata(self.root)
        write_json(self.root / "domains.json", {"domains": [DOMAIN]})
        self.add_entry("second", LISTING)
        with self.assertRaises(ValueError):
            load_catalog_metadata(self.root)

    def test_stale_designation_still_reserves_the_domain(self) -> None:
        provenance = self.root / "tools" / "tool" / "provenance.json"
        value = json.loads(provenance.read_text())
        value["source"]["commit"] = "b" * 40
        write_json(provenance, value)
        # Drift is a valid editorial state, not permission to award the slot twice.
        _, listings = load_catalog_metadata(self.root)
        pointer = read_json(self.root / "tools" / "tool" / "source.json", self.root)
        self.assertEqual(recommendation_state(pointer, value, listings["tool"]), "needs-review")
        self.add_entry("second", LISTING)
        with self.assertRaises(ValueError):
            load_catalog_metadata(self.root)

    def test_registry_types_and_required_fields_fail(self) -> None:
        invalid = [[], {"domains": {}}, {"domains": [None]}, {"domains": [True]}]
        for field in ("id", "label", "scope"):
            for bad in (None, False, 7, "", [], {}):
                invalid.append({"domains": [{**DOMAIN, field: bad}]})
            invalid.append({"domains": [{key: value for key, value in DOMAIN.items() if key != field}]})
        for value in invalid:
            with self.subTest(value=value):
                write_json(self.root / "domains.json", value)
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)

    def test_listing_types_and_required_fields_fail(self) -> None:
        invalid = [[], None, True, {}, {"domain": DOMAIN["id"]}, {"recommended": True}]
        for bad in (None, "true", 1, 0, [], {}):
            invalid.append({**LISTING, "recommended": bad})
        for bad in (None, False, 7, "", [], {}):
            invalid.append({**LISTING, "domain": bad})
        invalid.append({"domain": DOMAIN["id"], "recommended": True})
        for value in invalid:
            with self.subTest(value=value):
                write_json(self.root / "tools" / "tool" / "listing.json", value)
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)

    def test_reviewed_source_identity_validation(self) -> None:
        invalid = [None, [], True, {}]
        for field in ("repository", "path", "commit"):
            for bad in (None, False, 7, "", [], {}):
                invalid.append({**IDENTITY, field: bad})
            invalid.append({key: value for key, value in IDENTITY.items() if key != field})
        invalid.extend(
            [
                {**IDENTITY, "commit": "a" * 7},
                {**IDENTITY, "commit": "g" * 40},
                {**IDENTITY, "repository": "http://example.test/tool.git"},
                {**IDENTITY, "repository": "https://user:password@example.test/tool.git"},
                {**IDENTITY, "repository": "https://example.test/tool.git?secret=example"},
                {**IDENTITY, "path": "../tool"},
                {**IDENTITY, "path": "/tool"},
            ]
        )
        for identity in invalid:
            with self.subTest(identity=identity):
                write_json(self.root / "tools" / "tool" / "listing.json", {**LISTING, "reviewed_source": identity})
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)

    def test_malformed_json_fails_without_changing_files(self) -> None:
        for relative in ("domains.json", "tools/tool/listing.json"):
            with self.subTest(file=relative):
                target = self.root / relative
                original = target.read_bytes()
                target.write_bytes(b"{ broken\n")
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)
                self.assertEqual(target.read_bytes(), b"{ broken\n")
                target.write_bytes(original)

    def test_validation_never_renews_editorial_data(self) -> None:
        listing_file = self.root / "tools" / "tool" / "listing.json"
        before = listing_file.read_bytes()
        changed = copy.deepcopy(LISTING)
        changed["reviewed_source"]["commit"] = "b" * 40
        # A well-formed older review is valid metadata but not a renewed endorsement.
        write_json(listing_file, changed)
        old_review = listing_file.read_bytes()
        _, listings = load_catalog_metadata(self.root)
        self.assertEqual(listings["tool"], changed)
        self.assertEqual(listing_file.read_bytes(), old_review)
        self.assertNotEqual(old_review, before)

    def test_real_seed_domains_and_reviewed_sources_record_selected_revisions(self) -> None:
        expected_domains = {
            "test-environments": (
                "Test environments",
                "Create and operate isolated environments for testing software and reproducing failures.",
            ),
            "smart-tool-development": (
                "Smart Tool development",
                "Create, extend, check, and evaluate Smart Tools.",
            ),
        }
        registry = json.loads((ROOT / "domains.json").read_text())
        self.assertEqual(
            {domain["id"]: (domain["label"], domain["scope"]) for domain in registry["domains"]},
            expected_domains,
        )
        seeds = {
            "digital-twin-universe": ("test-environments", "900583d3bc40ea8c6363a9b53c2560a0cdc98b74"),
            "smart-tool-creator": ("smart-tool-development", "7337543a6a596b2f94a7cdc648b4a53e8cf44919"),
        }
        for slug, (domain, commit) in seeds.items():
            entry = ROOT / "tools" / slug
            listing = json.loads((entry / "listing.json").read_text())
            source = json.loads((entry / "source.json").read_text())
            self.assertEqual(listing["domain"], domain)
            self.assertIs(listing["recommended"], True)
            self.assertEqual(
                listing["reviewed_source"],
                {"repository": source["repository"], "path": source.get("path", "."), "commit": commit},
            )
            # Do not assert equality to today's provenance commit: refresh may
            # legitimately advance it without renewing the editorial review.
        self.assertEqual(len(list(ROOT.glob("tools/*/listing.json"))), 2)
        domains, listings = load_catalog_metadata(ROOT)
        self.assertEqual(set(domains), set(expected_domains))
        self.assertEqual(set(listings), set(seeds))

    def test_real_seeds_remain_valid_metadata_after_snapshot_refresh(self) -> None:
        seed_root = self.root / "seeds"
        write_json(seed_root / "domains.json", json.loads((ROOT / "domains.json").read_text()))
        for entry in ROOT.glob("tools/*/listing.json"):
            slug = entry.parent.name
            for name in ("source.json", "listing.json", "provenance.json", "SMART_TOOL.md"):
                destination = seed_root / "tools" / slug / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((entry.parent / name).read_bytes())
            listing_file = seed_root / "tools" / slug / "listing.json"
            before = listing_file.read_bytes()
            provenance_file = seed_root / "tools" / slug / "provenance.json"
            value = json.loads(provenance_file.read_text())
            value["source"]["commit"] = "b" * 40
            write_json(provenance_file, value)
            _, listings = load_catalog_metadata(seed_root)
            pointer = read_json(seed_root / "tools" / slug / "source.json", seed_root)
            manifest, provenance = read_snapshot(seed_root / "tools" / slug, seed_root)
            self.assertEqual(
                recommendation_state(pointer, provenance, listings[slug], bool(manifest)), "needs-review"
            )
            self.assertEqual(listing_file.read_bytes(), before)

    def test_cli_delegates_to_the_shared_validator(self) -> None:
        spec = importlib.util.spec_from_file_location("validate_catalog_cli", ROOT / "scripts" / "validate_catalog.py")
        assert spec and spec.loader
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        with patch("catalog_metadata.load_catalog_metadata") as shared, redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(["--catalog-root", str(self.root)]), 0)
        shared.assert_called_once_with(self.root.resolve())
        with (
            patch("catalog_metadata.load_catalog_metadata", side_effect=ValueError("invalid metadata")),
            redirect_stderr(io.StringIO()) as errors,
        ):
            self.assertEqual(cli.main(["--catalog-root", str(self.root)]), 1)
        self.assertIn("ERROR catalog: invalid metadata", errors.getvalue())

    def test_recommendation_requires_matching_pointer_review_and_snapshot(self) -> None:
        entry = self.root / "tools" / "tool"
        pointer = read_json(entry / "source.json", self.root)
        manifest, provenance = read_snapshot(entry, self.root)
        self.assertEqual(manifest["name"], "Tool")
        self.assertEqual(validate_pointer(pointer)["ref"], "main")
        self.assertEqual(catalog_sources(self.root), [entry / "source.json"])
        self.assertEqual(recommendation_state(pointer, provenance, LISTING), "recommended")
        self.assertEqual(recommendation_state(pointer, provenance, None), "ordinary")
        self.assertEqual(
            recommendation_state(pointer, provenance, {"domain": DOMAIN["id"], "recommended": False}),
            "ordinary",
        )
        self.assertEqual(recommendation_state(pointer, provenance, LISTING, False), "needs-review")
        self.assertEqual(recommendation_state(pointer, {}, LISTING), "needs-review")
        for field, value in (
            ("repository", "https://example.test/another.git"),
            ("path", "another"),
            ("ref", "feature"),
        ):
            with self.subTest(pointer_field=field):
                self.assertEqual(
                    recommendation_state({**pointer, field: value}, provenance, LISTING), "needs-review"
                )
        for field, value in (
            ("repository", "https://example.test/another.git"),
            ("path", "another"),
            ("commit", "b" * 40),
        ):
            changed = copy.deepcopy(LISTING)
            changed["reviewed_source"][field] = value
            with self.subTest(reviewed_field=field):
                self.assertEqual(recommendation_state(pointer, provenance, changed), "needs-review")

    def test_recommendation_drift_removes_rendered_badge_and_preference(self) -> None:
        self.add_entry("a-ordinary", None)
        before = rendered_catalog(self.root)
        cards = CatalogCards(before).cards
        self.assertEqual([card["slug"] for card in cards], ["tool", "a-ordinary"])
        self.assertEqual(cards[0]["badges"], [["recommendation", "recommended"]])
        listing_path = self.root / "tools" / "tool" / "listing.json"
        original = listing_path.read_bytes()
        provenance_path = self.root / "tools" / "tool" / "provenance.json"
        provenance = read_json(provenance_path, self.root)
        provenance["source"]["commit"] = "b" * 40
        write_json(provenance_path, provenance)
        after = rendered_catalog(self.root)
        cards = CatalogCards(after).cards
        self.assertEqual([card["slug"] for card in cards], ["a-ordinary", "tool"])
        self.assertEqual(cards[1]["domain"], DOMAIN["id"])
        self.assertEqual(cards[1]["badges"], [["recommendation", "needs-review"]])
        self.assertNotIn('class="recommendation recommended"', after)
        self.assertIn("Recommendation needs review", after)
        self.assertIn("No recommendation preference applies.", after)
        self.assertEqual(listing_path.read_bytes(), original)

    def test_pinned_fixture_renders_two_recommended_first_and_twenty_unclassified(self) -> None:
        # Construct isolated snapshots at the reviewed commits, independent of
        # live provenance. Only this initial-state fixture assumes two badges.
        pinned = self.root / "pinned"
        write_json(pinned / "domains.json", read_json(ROOT / "domains.json", ROOT))
        manifest_bytes = (self.root / "tools" / "tool" / "SMART_TOOL.md").read_bytes()
        for slug in ("digital-twin-universe", "smart-tool-creator"):
            listing = read_json(ROOT / "tools" / slug / "listing.json", ROOT)
            reviewed = listing["reviewed_source"]
            entry = pinned / "tools" / slug
            write_json(entry / "listing.json", listing)
            write_json(
                entry / "source.json",
                {field: reviewed[field] for field in ("repository", "path")} | {"ref": reviewed["commit"]},
            )
            write_json(
                entry / "provenance.json",
                {
                    "source": {**reviewed, "ref": reviewed["commit"]},
                    "original_manifest_path": "SMART_TOOL.md",
                    "last_success": "2026-10-07T03:38:13Z",
                },
            )
            (entry / "SMART_TOOL.md").write_bytes(manifest_bytes)
        for index in range(20):
            write_json(
                pinned / "tools" / f"a-unclassified-{index:02d}" / "source.json",
                {"repository": IDENTITY["repository"]},
            )
        document = rendered_catalog(pinned)
        cards = CatalogCards(document).cards
        self.assertEqual(len(cards), 22)
        self.assertEqual([card["slug"] for card in cards[:2]], ["digital-twin-universe", "smart-tool-creator"])
        self.assertEqual(
            [card["slug"] for card in cards if ["recommendation", "recommended"] in card["badges"]],
            ["digital-twin-universe", "smart-tool-creator"],
        )
        self.assertEqual(sum(card["domain"] == "" for card in cards), 20)
        self.assertIn('value="__unclassified__">Not yet classified', document)
        self.assertIn("22 tools", document)
        self.assertIn(DOMAIN["label"], document)
        self.assertIn("Smart Tool development", document)

    def test_real_catalog_renders_recorded_states_and_order_including_drift(self) -> None:
        # Refresh may advance live snapshots without renewing editorial review.
        # Derive expected badges and preference from the shared identity helper.
        domains, listings = load_catalog_metadata(ROOT)
        expected = []
        for source in catalog_sources(ROOT):
            slug = source.parent.name
            pointer = validate_pointer(read_json(source, ROOT))
            manifest, provenance = read_snapshot(source.parent, ROOT)
            listing = listings.get(slug)
            state = recommendation_state(pointer, provenance, listing, bool(manifest))
            expected.append(
                (
                    state != "recommended",
                    slug,
                    {
                        "slug": slug,
                        "domain": listing["domain"] if listing else ("" if domains is not None else None),
                        "badges": [] if state == "ordinary" else [["recommendation", state]],
                    },
                )
            )
        document = rendered_catalog(ROOT)
        self.assertEqual(CatalogCards(document).cards, [card for _, _, card in sorted(expected)])
        self.assertIn(f"{len(expected)} tools", document)


if __name__ == "__main__":
    unittest.main()