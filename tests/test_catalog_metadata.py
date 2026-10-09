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


CATEGORY = {"id": "test-environments", "label": "Test environments", "scope": "Isolated testing."}
IDENTITY = {"repository": "https://example.test/tool.git", "path": ".", "commit": "a" * 40}
# Synthetic reviewed metadata is test-only, never evidence of an actual review.
LISTING = {"category": CATEGORY["id"], "recommended": True, "reviewed_source": IDENTITY}
# Identities copied from pinned snapshot provenance, not live listing metadata.
# Pinning these test-only identities makes badge coverage independent of refresh.
PINNED_FIXTURE_SOURCES = {
    "digital-twin-universe": {
        "repository": "https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe.git",
        "path": ".",
        "commit": "900583d3bc40ea8c6363a9b53c2560a0cdc98b74",
    },
    "smart-tool-creator": {
        "repository": "https://github.com/microsoft/amplifier-smart-tool-creator.git",
        "path": ".",
        "commit": "7337543a6a596b2f94a7cdc648b4a53e8cf44919",
    },
}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n", encoding="utf-8")


class CatalogCards(HTMLParser):
    """Observe rendered card order, classification, and badges, not source code."""

    def __init__(self, document: str) -> None:
        super().__init__()
        self.cards: list[dict[str, object]] = []
        self.card: dict[str, object] | None = None
        self.checkboxes: list[dict[str, str | None]] = []
        self.labels: dict[str, str] = {}
        self.label_target: str | None = None
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.guide_heading: dict[str, object] | None = None
        self.in_guide_heading = False
        self.feed(document)

    def handle_starttag(self, tag: str, attributes: list[tuple[str, str | None]]) -> None:
        attrs = dict(attributes)
        if tag == "h2" and attrs.get("id") == "recommendation-guide-title":
            self.guide_heading = {"attrs": attrs, "ancestors": list(self.elements), "text": ""}
            self.in_guide_heading = True
        if tag not in ("area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"):
            self.elements.append((tag, attrs))
        if tag == "input" and attrs.get("type") == "checkbox":
            self.checkboxes.append(attrs)
        if tag == "label":
            self.label_target = attrs.get("for")
            if self.label_target:
                self.labels[self.label_target] = ""
        if tag == "article" and attrs.get("class") == "catalog-card":
            self.card = {"slug": attrs["data-tool"], "category": attrs.get("data-category"), "badges": []}
            self.cards.append(self.card)
        elif tag in ("span", "summary") and self.card is not None:
            classes = (attrs.get("class") or "").split()
            if "recommendation" in classes:
                self.card["badges"].append(classes)

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2":
            self.in_guide_heading = False
        for index in range(len(self.elements) - 1, -1, -1):
            if self.elements[index][0] == tag:
                del self.elements[index:]
                break
        if tag == "article":
            self.card = None
        if tag == "label":
            self.label_target = None

    def handle_data(self, data: str) -> None:
        if self.in_guide_heading and self.guide_heading is not None:
            self.guide_heading["text"] += data
        if self.label_target:
            self.labels[self.label_target] += data


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
        write_json(self.root / "categories.json", {"categories": [CATEGORY]})
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
        self.add_entry("alternative", {"category": CATEGORY["id"], "recommended": False})
        categories, listings = load_catalog_metadata(self.root)
        self.assertEqual(categories, {CATEGORY["id"]: CATEGORY})
        self.assertEqual(listings["tool"], LISTING)
        self.assertEqual(listings["alternative"], {"category": CATEGORY["id"], "recommended": False})

    def test_missing_metadata_preserves_legacy_catalog(self) -> None:
        (self.root / "categories.json").unlink()
        (self.root / "tools" / "tool" / "listing.json").unlink()
        self.assertEqual(load_catalog_metadata(self.root), (None, {}))

    def test_registry_with_unclassified_listing_is_valid(self) -> None:
        self.add_entry("unclassified", None)
        categories, listings = load_catalog_metadata(self.root)
        self.assertEqual(categories, {CATEGORY["id"]: CATEGORY})
        self.assertNotIn("unclassified", listings)

    def test_new_pointer_does_not_require_a_generated_snapshot(self) -> None:
        entry = self.add_entry("new-tool", None)
        (entry / "SMART_TOOL.md").unlink()
        (entry / "provenance.json").unlink()
        _, listings = load_catalog_metadata(self.root)
        self.assertNotIn("new-tool", listings)

    def test_unknown_category_and_listing_without_registry_fail(self) -> None:
        write_json(self.root / "tools" / "tool" / "listing.json", {**LISTING, "category": "self-awarded"})
        with self.assertRaisesRegex(ValueError, "category"):
            load_catalog_metadata(self.root)
        write_json(self.root / "tools" / "tool" / "listing.json", LISTING)
        (self.root / "categories.json").unlink()
        with self.assertRaisesRegex(ValueError, r"categories\.json"):
            load_catalog_metadata(self.root)

    def test_duplicate_category_and_second_designation_fail(self) -> None:
        write_json(self.root / "categories.json", {"categories": [CATEGORY, CATEGORY]})
        with self.assertRaises(ValueError):
            load_catalog_metadata(self.root)
        write_json(self.root / "categories.json", {"categories": [CATEGORY]})
        self.add_entry("second", LISTING)
        with self.assertRaises(ValueError):
            load_catalog_metadata(self.root)

    def test_stale_designation_still_reserves_the_category(self) -> None:
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
        invalid = [[], {"categories": {}}, {"categories": [None]}, {"categories": [True]}]
        for field in ("id", "label", "scope"):
            for bad in (None, False, 7, "", [], {}):
                invalid.append({"categories": [{**CATEGORY, field: bad}]})
            invalid.append({"categories": [{key: value for key, value in CATEGORY.items() if key != field}]})
        for value in invalid:
            with self.subTest(value=value):
                write_json(self.root / "categories.json", value)
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)

    def test_listing_types_and_required_fields_fail(self) -> None:
        invalid = [[], None, True, {}, {"category": CATEGORY["id"]}, {"recommended": True}]
        for bad in (None, "true", 1, 0, [], {}):
            invalid.append({**LISTING, "recommended": bad})
        for bad in (None, False, 7, "", [], {}):
            invalid.append({**LISTING, "category": bad})
        invalid.append({"category": CATEGORY["id"], "recommended": True})
        for value in invalid:
            with self.subTest(value=value):
                write_json(self.root / "tools" / "tool" / "listing.json", value)
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)

    def test_only_one_primary_category_and_no_duplicate_evidence_fields(self) -> None:
        for value in (
            {**LISTING, "category": [CATEGORY["id"]]},
            {**LISTING, "categories": [CATEGORY["id"]]},
            {**LISTING, "review_evidence": "https://example.test/review"},
            {**LISTING, "review_status": "passed"},
            {"category": CATEGORY["id"], "recommended": False, "reviewed_source": IDENTITY},
        ):
            with self.subTest(value=value):
                write_json(self.root / "tools" / "tool" / "listing.json", value)
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)

    def test_registry_is_flat_and_closed(self) -> None:
        for category in (
            {**CATEGORY, "children": []},
            {**CATEGORY, "parent": "other"},
            {**CATEGORY, "id": "Invalid ID"},
        ):
            with self.subTest(category=category):
                write_json(self.root / "categories.json", {"categories": [category]})
                with self.assertRaises(ValueError):
                    load_catalog_metadata(self.root)

    def test_structural_validation_does_not_establish_maintainer_authority(self) -> None:
        # A valid designation alone cannot distinguish a maintainer decision
        # from creator-authored metadata. Authorization is the documented merge
        # gate, not a runtime claim made by the schema validator.
        _, listings = load_catalog_metadata(self.root)
        self.assertEqual(listings["tool"], LISTING)

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
        for relative in ("categories.json", "tools/tool/listing.json"):
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
        registry_file = self.root / "categories.json"
        registry_before = registry_file.read_bytes()
        before = listing_file.read_bytes()
        changed = copy.deepcopy(LISTING)
        changed["reviewed_source"]["commit"] = "b" * 40
        # A well-formed older review is valid metadata but not a renewed endorsement.
        write_json(listing_file, changed)
        old_review = listing_file.read_bytes()
        _, listings = load_catalog_metadata(self.root)
        self.assertEqual(listings["tool"], changed)
        self.assertEqual(listing_file.read_bytes(), old_review)
        self.assertEqual(registry_file.read_bytes(), registry_before)
        self.assertNotEqual(old_review, before)

    def test_real_initial_choices_are_classified_without_reviewed_sources(self) -> None:
        expected_categories = {
            "test-environments": (
                "Test environments",
                "Create and operate isolated environments for testing software and reproducing failures.",
            ),
            "smart-tool-development": (
                "Smart Tool development",
                "Create, extend, check, and evaluate Smart Tools.",
            ),
        }
        registry = json.loads((ROOT / "categories.json").read_text())
        self.assertEqual(
            {category["id"]: (category["label"], category["scope"]) for category in registry["categories"]},
            expected_categories,
        )
        seeds = {
            "digital-twin-universe": "test-environments",
            "smart-tool-creator": "smart-tool-development",
        }
        for slug, category in seeds.items():
            entry = ROOT / "tools" / slug
            listing = json.loads((entry / "listing.json").read_text())
            self.assertEqual(listing, {"category": category, "recommended": False})
            self.assertNotIn("reviewed_source", listing)
        self.assertEqual(len(list(ROOT.glob("tools/*/listing.json"))), 2)
        categories, listings = load_catalog_metadata(ROOT)
        self.assertEqual(set(categories), set(expected_categories))
        self.assertEqual(set(listings), set(seeds))

    def test_real_seeds_remain_valid_metadata_after_snapshot_refresh(self) -> None:
        seed_root = self.root / "seeds"
        write_json(seed_root / "categories.json", json.loads((ROOT / "categories.json").read_text()))
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
                recommendation_state(pointer, provenance, listings[slug], bool(manifest)), "ordinary"
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

    def test_cli_help_describes_category_metadata(self) -> None:
        spec = importlib.util.spec_from_file_location("validate_catalog_cli", ROOT / "scripts" / "validate_catalog.py")
        assert spec and spec.loader
        cli = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cli)
        with redirect_stdout(io.StringIO()) as output, self.assertRaises(SystemExit) as result:
            cli.main(["--help"])
        self.assertEqual(result.exception.code, 0)
        self.assertIn("optional categories.json", " ".join(output.getvalue().split()))

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
            recommendation_state(pointer, provenance, {"category": CATEGORY["id"], "recommended": False}),
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
        self.assertEqual(cards[1]["category"], CATEGORY["id"])
        self.assertEqual(cards[1]["badges"], [["recommendation", "needs-review"]])
        self.assertNotIn('class="recommendation recommended"', after)
        self.assertIn("Recommendation needs review", after)
        self.assertIn("No recommendation preference applies.", after)
        self.assertEqual(listing_path.read_bytes(), original)

    def test_recommended_only_checkbox_is_named_and_unchecked_by_default(self) -> None:
        controls = CatalogCards(rendered_catalog(self.root))
        recommended_only = [
            checkbox for checkbox in controls.checkboxes
            if checkbox.get("aria-label") == "Recommended only"
            or controls.labels.get(checkbox.get("id", ""), "").strip() == "Recommended only"
        ]
        self.assertEqual(len(recommended_only), 1)
        self.assertNotIn("checked", recommended_only[0])

    def test_recommended_disclosure_explains_recorded_revision_and_limits(self) -> None:
        document = rendered_catalog(self.root)
        self.assertIn('<details class="recommendation-disclosure">', document)
        self.assertIn('<summary class="recommendation recommended">Recommended</summary>', document)
        self.assertIn(f'<code>{IDENTITY["commit"]}</code>', document)
        self.assertIn("Not certification or proof of host readiness.", document)
        heading = CatalogCards(document).guide_heading
        self.assertIsNotNone(heading)
        self.assertEqual(heading["text"].strip(), "What does Recommended mean?")
        self.assertTrue(any(
            tag == "section" and attrs.get("aria-labelledby") == "recommendation-guide-title"
            for tag, attrs in heading["ancestors"]
        ))
        for tag, attrs in [*heading["ancestors"], ("h2", heading["attrs"])]:
            self.assertNotEqual(tag, "details", "The guide must be outside disclosures.")
            self.assertNotIn("hidden", attrs)
            self.assertNotEqual(attrs.get("aria-hidden"), "true")
        for explanation in (
            "specification conformance, representative-task evidence, and documented limitations",
            "Compare documented capabilities, platform support, and prerequisites with your task first.",
            "Recommended is a preference among suitable options, not an override; consider suitable alternatives.",
            "Unclassified or undesignated tools are not a negative quality judgment.",
            "“Recommended only” is optional and starts unchecked, so all tools remain visible by default.",
        ):
            self.assertIn(explanation, document)

    def test_pinned_fixture_renders_two_recommended_first_and_twenty_unclassified(self) -> None:
        # Fake-reviewed metadata in isolated fixtures exercises rendering only.
        # It is not evidence of review or endorsement of the real initial choices.
        pinned = self.root / "pinned"
        write_json(pinned / "categories.json", read_json(ROOT / "categories.json", ROOT))
        manifest_bytes = (self.root / "tools" / "tool" / "SMART_TOOL.md").read_bytes()
        fixture_categories = {
            "digital-twin-universe": "test-environments",
            "smart-tool-creator": "smart-tool-development",
        }
        for slug, category in fixture_categories.items():
            reviewed = copy.deepcopy(PINNED_FIXTURE_SOURCES[slug])
            listing = {"category": category, "recommended": True, "reviewed_source": reviewed}
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
        self.assertEqual(sum(card["category"] == "" for card in cards), 20)
        self.assertIn('value="__unclassified__">Not yet classified', document)
        self.assertIn("22 tools", document)
        self.assertIn(CATEGORY["label"], document)
        self.assertIn("Smart Tool development", document)
        self.assertEqual(document.count('data-recommended="true"'), 2)
        self.assertEqual(document.count('data-recommended="false"'), 20)

    def test_real_catalog_renders_recorded_states_and_order_including_drift(self) -> None:
        # Refresh may advance live snapshots without renewing editorial review.
        # Derive expected badges and preference from the shared identity helper.
        categories, listings = load_catalog_metadata(ROOT)
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
                        "category": listing["category"] if listing else ("" if categories is not None else None),
                        "badges": [] if state == "ordinary" else [["recommendation", state]],
                    },
                )
            )
        document = rendered_catalog(ROOT)
        cards = CatalogCards(document).cards
        self.assertEqual(cards, [card for _, _, card in sorted(expected)])
        self.assertIn(f"{len(expected)} tools", document)
        self.assertEqual(len(cards), 22)
        self.assertEqual(sum(bool(card["category"]) for card in cards), 2)
        self.assertEqual(sum(card["category"] == "" for card in cards), 20)
        self.assertTrue(all(not card["badges"] for card in cards))
        self.assertNotIn('data-recommended="true"', document)


if __name__ == "__main__":
    unittest.main()