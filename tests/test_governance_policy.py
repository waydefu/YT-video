"""Minimal always-run governance checks. Never mislabel as aesthetic/playback QA.

Only stdlib used so docs-only PRs do not require Blender, browser or python-pptx.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GovernancePolicyTests(unittest.TestCase):
    def read(self, path):
        return (ROOT / path).read_text(encoding="utf-8")

    def test_mandatory_entrypoints_exist(self):
        required = (
            "AGENTS.md",
            "README.md",
            "docs/QUALITY-GATED-WORKFLOW.md",
            "docs/WORKFLOW-EXPLAINER-DECK.md",
            "docs/GOVERNANCE-STATUS.md",
            "docs/SHOTLIST.md",
            "docs/archive/SHOTLIST-V3-LEGACY.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/workflows/governance.yml",
        )
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((ROOT / name).is_file(), name)

    def test_active_vs_archived_creative_contract(self):
        active = self.read("docs/SHOTLIST.md")
        archive = self.read("docs/archive/SHOTLIST-V3-LEGACY.md")
        self.assertIn("重低音開燈聲", active)
        self.assertIn("粉塵", active)
        self.assertIn("時間反轉", active)
        self.assertIn("archive/SHOTLIST-V3-LEGACY.md", active)
        self.assertIn("HISTORICAL / NOT CURRENT", archive)

    def test_agents_starts_with_governance_gates(self):
        agents = self.read("AGENTS.md")
        self.assertIn("QUALITY-GATED-WORKFLOW.md", agents)
        self.assertIn("docs/GOVERNANCE-STATUS.md", agents)
        self.assertIn("SHOTLIST-V3-LEGACY", agents)
        self.assertIn("G3 BLOCKED / NOT RUN", agents)

    def test_ci_gate_runs_on_all_prs_without_paths_filter(self):
        wf = self.read(".github/workflows/governance.yml")
        self.assertIn("pull_request:", wf)
        self.assertIn("push:", wf)
        self.assertNotIn("paths:", wf)
        self.assertIn("permissions:", wf)
        self.assertIn("test_docs_links.py", wf)
        self.assertIn("test_governance_policy.py", wf)

    def test_no_stale_anatomy_ci_claim(self):
        anatomy = self.read("docs/ANATOMY-EXPLAINER.md")
        ci_rows = [s for s in anatomy.splitlines() if s.startswith("| CI |")]
        self.assertEqual(len(ci_rows), 1)
        self.assertNotIn("尚未執行", ci_rows[0],
                         "Historical CI success must not be reported as NOT RUN")
        self.assertIn("42230737798", ci_rows[0])

    def test_readme_has_curated_status(self):
        readme = self.read("README.md")
        self.assertIn("docs/GOVERNANCE-STATUS.md", readme)
        self.assertIn("docs/SHOTLIST.md", readme)
        self.assertIn("未實播", readme)


if __name__ == "__main__":
    unittest.main()
