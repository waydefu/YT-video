"""Consistency of the YouTube cut: narration timing, deck structure and the numbers shown on screen.

Layer A only. It proves the script, timings and figures agree with each other and with ai_subscriptions_data.py; it does
not prove the figures match the vendors (the user cross-checked them against official pages on 2026-11-10) or how
PowerPoint plays the transitions.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ai_subscriptions_data as D  # noqa: E402
import ai_subscriptions_script as S  # noqa: E402

try:
    import build_ai_subscriptions_youtube as Y
except ImportError:  # python-pptx missing
    Y = None


class Script(unittest.TestCase):
    def test_total_matches_the_storyboard(self):
        self.assertEqual(S.TOTAL_SECONDS, 645)  # 10:45 in the user's Doc

    def test_speaking_rate_is_plausible(self):
        for sid, _, sec, text in S.SCENES:
            rate = len(text) / sec
            self.assertTrue(2.0 <= rate <= 5.5, f"{sid}: {rate:.1f} chars/s")

    def test_narration_numbers_match_the_data(self):
        self.assertIn("一點九二六", S.NARRATION["s13"])
        self.assertAlmostEqual(D.cost_per_100m(D.DEEPSEEK["V4.1 Flash"]["offpeak"]), 1.926, places=6)
        one, ref = D.OPENCODE_EXAMPLE
        self.assertAlmostEqual(one / ref * 100, 6.67, places=2)
        self.assertEqual(D.KIMI_TIERS_CNY, {"Go": 49, "Plus": 99})


@unittest.skipIf(Y is None, "python-pptx not installed")
class Deck(unittest.TestCase):
    def test_every_scene_has_slides_and_holds_sum_to_the_script(self):
        slides = Y.deck()
        scenes = {scene for _, scene, *_ in slides}
        self.assertEqual(scenes, set(S.SCENE_SECONDS))
        holds = Y.holds_ms(slides)
        self.assertAlmostEqual(sum(holds) / 1000, S.TOTAL_SECONDS, delta=1.0)
        self.assertTrue(all(h >= 5000 for h in holds))  # never a flash

    def test_keys_unique_and_first_slide_has_no_transition(self):
        slides = Y.deck()
        keys = [k for k, *_ in slides]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertIsNone(slides[0][3])

    def test_device_mix(self):
        kinds = {kind for _, _, _, kind, _ in Y.deck()}
        self.assertTrue({"stay", "pan_right", "nest", "zoom_out"} <= kinds)


if __name__ == "__main__":
    unittest.main()
