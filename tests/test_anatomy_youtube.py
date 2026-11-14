"""Anatomy YouTube cut: narration timing, deck structure and the morphing chapter navigation.

Layer A only. The deck test needs the official assets (scripts/anatomy_assets.py output) and is skipped without them.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import anatomy_script as S  # noqa: E402

try:
    import build_anatomy_youtube as A
except ImportError:  # python-pptx missing
    A = None

ASSETS = ROOT / "build" / "anatomy" / "assets"


class Script(unittest.TestCase):
    def test_total_matches_the_storyboard(self):
        self.assertEqual(S.TOTAL_SECONDS, 475)  # 7:55 in the user's Doc

    def test_speaking_rate_is_plausible(self):
        for sid, _, sec, text in S.SCENES:
            self.assertTrue(2.0 <= len(text) / sec <= 5.5, f"{sid}: {len(text) / sec:.1f} chars/s")

    def test_chapters_cover_every_scene_in_order(self):
        idx = [ch for _, ch, _, _ in S.SCENES]
        self.assertEqual(idx, sorted(idx))
        self.assertEqual(set(idx), set(range(len(S.CHAPTERS))))

    def test_no_hands_on_claims_in_the_narration(self):
        text = "".join(t for *_, t in S.SCENES)
        for banned in ("我們測試", "實測 FPS", "親自"):
            self.assertNotIn(banned, text)
        self.assertIn("不是我們的實測", S.NARRATION["s01"])  # "實測" appears only as a disclaimer


@unittest.skipIf(A is None or not (ASSETS / "LICENSE_ANATOMY.txt").is_file(), "python-pptx or official assets missing")
class Deck(unittest.TestCase):
    def test_every_scene_has_slides_and_time_adds_up(self):
        slides = A.deck(A.Art(ASSETS))
        self.assertEqual({scene for _, scene, *_ in slides}, set(S.SCENE_SECONDS))
        total = (sum(A.holds_ms(slides)) + sum(A.durations_ms(slides))) / 1000
        self.assertAlmostEqual(total, S.TOTAL_SECONDS, delta=1.0)
        self.assertTrue(all(h >= 3000 for h in A.holds_ms(slides)))

    def test_menu_slide_exists_before_the_rail_and_keys_are_unique(self):
        slides = A.deck(A.Art(ASSETS))
        keys = [k for k, *_ in slides]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIn("menu", keys)
        self.assertEqual(keys.index("menu"), 2)  # after the two hook slides
        self.assertIsNone(slides[0][3])


if __name__ == "__main__":
    unittest.main()
