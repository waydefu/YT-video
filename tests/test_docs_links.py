"""Documentation hygiene: relative Markdown links resolve and referenced repo paths exist.

Proportionate check for docs-only changes (layer A for documents). It proves that links and file
references are not dangling; it says nothing about whether the documents are correct.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = [ROOT / "README.md", ROOT / "AGENTS.md", ROOT / ".github/PULL_REQUEST_TEMPLATE.md",
        *sorted((ROOT / "docs").glob("*.md")), *sorted((ROOT / ".agents/skills").glob("*/SKILL.md"))]
LINK = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
REF = re.compile(r"`((?:scripts|docs|tests|\.github|\.agents|config|blender)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)`")
GENERATED = ("build/", "assets/external/")


class DocLinks(unittest.TestCase):
    def test_relative_links_resolve(self):
        broken = []
        for doc in DOCS:
            for target in LINK.findall(doc.read_text(encoding="utf-8")):
                if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                    continue
                if not (doc.parent / target).resolve().exists():
                    broken.append(f"{doc.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [], "\n".join(broken))

    def test_referenced_repo_paths_exist(self):
        missing = []
        for doc in DOCS:
            for ref in REF.findall(doc.read_text(encoding="utf-8")):
                if "*" in ref or ref.startswith(GENERATED) or "…" in ref:
                    continue
                if not (ROOT / ref).exists():
                    missing.append(f"{doc.relative_to(ROOT)} mentions {ref}")
        self.assertEqual(missing, [], "\n".join(missing))

    def test_new_workflow_is_linked_from_entry_points(self):
        for doc in ("README.md", "AGENTS.md", "docs/QUALITY-GATED-WORKFLOW.md",
                    ".agents/skills/powerpoint-cinematic/SKILL.md", ".agents/skills/quality-gated-production/SKILL.md"):
            self.assertIn("WORKFLOW-EXPLAINER-DECK", (ROOT / doc).read_text(encoding="utf-8"), doc)


if __name__ == "__main__":
    unittest.main()
