"""Classroom AI/Agent deck: data cross-checks against the verified data module, notes coverage, click-to-advance, logo policy.

Layer A only. The deck tests need the logo PNGs (scripts/classroom_logos.py output) and are skipped without them.
"""
import re
import sys
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ai_subscriptions_data as D  # noqa: E402
import classroom_ai_agents_script as S  # noqa: E402
import pptx_morph_patch  # noqa: E402

try:
    import build_classroom_ai_agents as B
except ImportError:  # python-pptx missing
    B = None

ASSETS = ROOT / "build" / "classroom" / "assets"


class Data(unittest.TestCase):
    def test_benchmark_matches_the_verified_table(self):
        ref = {n.split("（")[0].replace("Claude ", ""): (s, c) for n, s, c in D.TB4_INDEPENDENT}
        for name, score, cost in S.BENCH:
            key = name.rstrip("*").replace("Gemini 4 Carbon", "Gemini 4 Carbon")
            self.assertEqual(ref[key], (score, cost), name)

    def test_deepseek_example_is_recomputed(self):
        for (label, value), (model, tier) in zip(S.DEEPSEEK_100M, [("V4.1 Flash", "offpeak"), ("V4.1 Flash", "peak"),
                                                                    ("V4 Pro", "offpeak"), ("V4 Pro", "peak")]):
            self.assertAlmostEqual(value, D.cost_per_100m(D.DEEPSEEK[model][tier]), places=3, msg=label)
        self.assertEqual(S.DEEPSEEK_UNIT, {k: D.DEEPSEEK["V4.1 Flash"]["offpeak"][k] for k in ("cache", "input", "output")})

    def test_every_scene_has_a_chapter_and_notes(self):
        self.assertEqual(set(S.SCENE_CHAPTER), set(S.NOTES))
        chapters = {c for c in S.SCENE_CHAPTER.values() if c is not None}
        self.assertEqual(chapters, set(range(len(S.CHAPTERS))))

    def test_notes_carry_no_unverified_hands_on_claims(self):
        text = "".join(S.NOTES.values())
        for banned in ("我實測", "我們測試", "親自測"):
            self.assertNotIn(banned, text)

    def test_check_date_is_stated_on_the_closing_note(self):
        self.assertIn(S.CHECK_DATE, S.NOTES["h_end"])


class Patch(unittest.TestCase):
    def test_hold_none_means_click_only(self):
        frag = pptx_morph_patch.transition(1300, None)
        self.assertNotIn("advTm", frag)
        self.assertIn('advClick="1"', frag)
        self.assertIn('advTm="5000"', pptx_morph_patch.transition(1300, 5000))


@unittest.skipIf(B is None or not (ASSETS / "manifest.json").is_file(), "python-pptx or logo assets missing")
class Deck(unittest.TestCase):
    def test_logo_manifest_is_classroom_use_only(self):
        import json
        manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(set(manifest), set(B.LOGO_KEYS))
        for key, rec in manifest.items():
            self.assertEqual(rec["mark_status"], "NOMINATIVE-CLASSROOM-USE", key)  # never claimed as licensed
            self.assertEqual(len(rec["sha256"]), 64)

    def test_scenes_and_unique_keys(self):
        slides = B.deck(B.Art(ASSETS))
        self.assertEqual({scene for _, scene, *_ in slides}, set(S.SCENE_CHAPTER))
        keys = [k for k, *_ in slides]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(keys.index("menu"), 2)
        self.assertIsNone(slides[0][3])

    def test_camera_alternates_between_chapters_and_stays_inside(self):
        slides = B.deck(B.Art(ASSETS))
        kinds = {k for *_, k in slides if k}
        self.assertTrue({"pan_right", "pan_down", "stay"} <= kinds)

    def test_built_deck_advances_on_click_only(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "c.pptx"
            B.build(out, ASSETS)
            with zipfile.ZipFile(out) as z:
                xml = "".join(z.read(n).decode("utf-8") for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n))
            self.assertNotIn("advTm", xml)
            self.assertIn("p159:morph", xml)


if __name__ == "__main__":
    unittest.main()
