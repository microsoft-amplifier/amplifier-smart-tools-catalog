"""Regression checks for preview retention and trusted-main publication gates."""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from types import SimpleNamespace

import yaml


WORKFLOW = (Path(__file__).resolve().parents[1] / ".github" / "workflows" / "website.yml").read_text()


def condition(job: str, **overrides: object) -> bool:
    """Evaluate the workflow's own boolean condition, not a duplicated policy."""
    match = re.search(rf"(?m)^  {job}:\n    if: >-\n((?:      .*\n)+)", WORKFLOW)
    assert match, f"Missing folded {job} condition"
    expression = " ".join(line.strip() for line in match[1].splitlines())
    expression = expression.replace("&&", " and ").replace("||", " or ")
    values = {
        "event_name": "workflow_run",
        "ref": "refs/heads/main",
        "repository": "example/catalog",
        "head_repository": "example/catalog",
        "head_branch": "main",
        "run_event": "schedule",
        "conclusion": "success",
        "publish": False,
        "build_result": "success",
    }
    values.update(overrides)
    github = SimpleNamespace(
        event_name=values["event_name"],
        ref=values["ref"],
        repository=values["repository"],
        event=SimpleNamespace(workflow_run=SimpleNamespace(
            head_repository=SimpleNamespace(full_name=values["head_repository"]),
            head_branch=values["head_branch"],
            event=values["run_event"],
            conclusion=values["conclusion"],
        )),
    )
    return bool(eval(expression, {"__builtins__": {}}, {
        "github": github,
        "inputs": SimpleNamespace(publish=values["publish"]),
        "needs": SimpleNamespace(build=SimpleNamespace(result=values["build_result"])),
    }))


class WebsiteWorkflowTests(unittest.TestCase):
    def test_refresh_success_and_failure_rebuild_validated_main(self) -> None:
        for outcome in ("success", "failure"):
            for event in ("push", "schedule", "workflow_dispatch"):
                with self.subTest(outcome=outcome, event=event):
                    self.assertTrue(condition("build", conclusion=outcome, run_event=event))
                    self.assertTrue(condition("deploy", conclusion=outcome, run_event=event))
        self.assertIn("ref: ${{ github.event_name == 'workflow_run' && 'main' || github.ref }}", WORKFLOW)
        self.assertIn("needs: build", WORKFLOW)
        self.assertNotIn("actions/download-artifact", WORKFLOW)
        self.assertNotIn("workflow_run.head_sha", WORKFLOW)
        self.assertNotIn("pull_request_target", WORKFLOW)

    def test_untrusted_or_non_main_refresh_is_not_built(self) -> None:
        for overrides in (
            {"head_repository": "outsider/catalog"},
            {"head_branch": "feature"},
            {"run_event": "pull_request"},
            {"run_event": "unknown"},
            {"conclusion": "cancelled"},
            {"conclusion": "skipped"},
        ):
            with self.subTest(overrides=overrides):
                self.assertFalse(condition("build", **overrides))
        self.assertFalse(condition("deploy", build_result="failure"))
        self.assertFalse(condition("deploy", build_result="skipped"))

    def test_prs_and_manual_branch_previews_never_deploy(self) -> None:
        self.assertTrue(condition("build", event_name="pull_request", ref="refs/pull/1/merge"))
        self.assertFalse(condition("deploy", event_name="pull_request", ref="refs/pull/1/merge", publish=True))
        self.assertFalse(condition("deploy", event_name="workflow_dispatch", ref="refs/heads/feature", publish=True))
        self.assertFalse(condition("deploy", event_name="workflow_dispatch", publish=False))
        self.assertTrue(condition("deploy", event_name="workflow_dispatch", publish=True))
        self.assertTrue(condition("deploy", event_name="push"))
        self.assertFalse(condition("deploy", event_name="push", ref="refs/heads/feature"))

    def test_metadata_scripts_tests_and_review_artifacts_are_included(self) -> None:
        for path in ("'categories.json'", "'scripts/**'", "'tests/**'", "'tools/**'", "'site/**'"):
            self.assertEqual(WORKFLOW.count(path), 2, path)
        self.assertIn("actions/upload-pages-artifact@v3", WORKFLOW)
        self.assertIn("retention-days: 7", WORKFLOW)
        self.assertIn("persist-credentials: false", WORKFLOW)

    def test_workflow_yaml_parses_with_category_triggers_and_preview_retention(self) -> None:
        # BaseLoader keeps the GitHub Actions "on" key rather than treating it
        # as a YAML 1.1 boolean. Existing condition tests exercise trust gates.
        workflow = yaml.load(WORKFLOW, Loader=yaml.BaseLoader)
        for event in ("push", "pull_request"):
            self.assertIn("categories.json", workflow["on"][event]["paths"])
        steps = workflow["jobs"]["build"]["steps"]
        upload = next(step for step in steps if step.get("uses") == "actions/upload-pages-artifact@v3")
        self.assertEqual(upload["with"]["retention-days"], "7")
        self.assertEqual(upload["with"]["path"], "_site")
        self.assertEqual(workflow["jobs"]["deploy"]["needs"], "build")


if __name__ == "__main__":
    unittest.main()