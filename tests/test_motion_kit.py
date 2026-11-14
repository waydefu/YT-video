"""Motion-kit checks: pure layout maths, rotation support in the world, per-slide Morph durations, proxy rotation.

Layer A only. They prove the geometry and the plumbing; they do not prove how PowerPoint tweens rotation or font size.
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from pptx import Presentation
    from pptx.util import Emu
except ImportError:  # pragma: no cover
    Presentation = None

if Presentation is not None:
    import build_motion_kit_demo as demo
    import deck_motion as M
    import pptx_morph_patch
    import pptx_morph_proxy
    from pptx_world import EMU, H, W, World


@unittest.skipIf(Presentation is None, "python-pptx not installed")
class Geometry(unittest.TestCase):
    def test_mix_hex(self):
        self.assertEqual(M.mix_hex("000000", "FFFFFF", 0.0), "000000")
        self.assertEqual(M.mix_hex("000000", "FFFFFF", 1.0), "FFFFFF")
        self.assertEqual(M.mix_hex("FF0000", "0000FF", 0.5), "800080")
        self.assertEqual(M.mix_hex("112233", "FFFFFF", 7.0), "FFFFFF")  # clamped

    def test_ripple_rings_fan_out_evenly(self):
        r = M.ripple_radii(4, 0.5, 8.0)
        self.assertEqual(r, [1.0, 2.0, 3.0, 4.0])
        self.assertEqual(M.ripple_radii(3, 0.0, 9.0), [0.0, 0.0, 0.0])

    def test_ring_starts_at_twelve_o_clock_and_keeps_its_radius(self):
        pts = M.ring_layout(6, 10.0, 5.0, 2.0)
        self.assertAlmostEqual(pts[0][0], 10.0)
        self.assertAlmostEqual(pts[0][1], 3.0)
        for x, y in pts:
            self.assertAlmostEqual(((x - 10) ** 2 + (y - 5) ** 2) ** 0.5, 2.0)

    def test_column_is_evenly_spaced(self):
        pts = M.column_layout(4, 1.0, 2.0, 0.9)
        self.assertEqual([round(y, 6) for _, y in pts], [2.0, 2.9, 3.8, 4.7])
        self.assertTrue(all(x == 1.0 for x, _ in pts))

    def test_wheel_active_item_rests_and_others_tilt_shrink_fade(self):
        w = M.wheel_layout(6, 2, 7.0, 3.75, 3.4, step_deg=20.0)
        a = w[2]
        self.assertTrue(a["active"])
        self.assertAlmostEqual(a["x"], 7.0 - 3.4)
        self.assertAlmostEqual(a["y"], 3.75)
        self.assertEqual((a["rot"], a["fade"]), (0.0, 0.0))
        self.assertAlmostEqual(w[3]["rot"], 20.0)
        self.assertAlmostEqual(w[1]["rot"], -20.0)
        self.assertGreater(w[3]["y"], a["y"])
        self.assertLess(w[1]["y"], a["y"])
        self.assertGreater(a["pt"], w[3]["pt"])
        self.assertGreater(w[3]["pt"], w[5]["pt"])
        self.assertGreater(w[5]["fade"], w[3]["fade"])
        self.assertAlmostEqual(w[3]["y"] - a["y"], a["y"] - w[1]["y"])  # symmetric

    def test_roll_rests_at_the_spot_and_neighbours_wait_a_step_away(self):
        r = M.roll_layout(3, 1, 1.2, 2.0, 5.4, -20.0)
        self.assertEqual((r[1]["x"], r[1]["y"], r[1]["rot"]), (1.2, 2.0, 0.0))
        self.assertAlmostEqual(r[2]["y"], 7.4)  # just below a 7.5 in slide
        self.assertAlmostEqual(r[0]["y"], -3.4)
        self.assertEqual(r[2]["rot"], -20.0)

    def test_shuffle_states(self):
        tidy, dealt, again = (M.shuffle_layout(2, 2, 3.5, 1.7, 3.2, 2.0, 0.3, s) for s in (0, 1, 2))
        self.assertTrue(all(c[4] == 0.0 for c in tidy))
        self.assertEqual(tidy, again)
        self.assertTrue(all(abs(c[4]) == 7.0 for c in dealt))
        self.assertNotEqual(dealt[0][4], dealt[1][4])  # neighbours turn opposite ways
        self.assertTrue(dealt[0][0] > tidy[0][0] and dealt[3][0] < tidy[3][0])  # nudged towards the centre


@unittest.skipIf(Presentation is None, "python-pptx not installed")
class Plumbing(unittest.TestCase):
    def deck(self, rots, durs=None):
        w = World(gap=0.6)
        for i, rot in enumerate(rots):
            def draw(c, rot=rot):
                c.rect("box", 3.0, 2.0, 2.0, 1.0, "FF0000", rot=rot)
                c.text("t", "字", 6.0, 2.0, 2.0, 1.0, 24, "000000", "Noto Sans CJK TC", "Noto Sans CJK TC", rot=rot)
            if i == 0:
                w.first(draw)
            else:
                w.add(draw, "stay", dur=(durs or [None] * len(rots))[i])
        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(int(W * EMU)), Emu(int(H * EMU))
        w.build(prs)
        return w, prs

    def test_rotation_reaches_the_shape_and_the_text_box(self):
        _, prs = self.deck([0, 30])
        shapes = {s.name: s for s in prs.slides[1].shapes}
        self.assertAlmostEqual(shapes["!!P00_box"].rotation, 30.0)
        self.assertAlmostEqual(shapes["!!P00_t"].rotation, 30.0)
        self.assertEqual({s.name: s.rotation for s in prs.slides[0].shapes}["!!P00_box"], 0.0)

    def test_negative_rotation_is_wrapped(self):
        _, prs = self.deck([0, -20])
        self.assertAlmostEqual({s.name: s for s in prs.slides[1].shapes}["!!P00_box"].rotation, 340.0)

    def test_world_durations_default_and_override(self):
        w, _ = self.deck([0, 10, 20], durs=[None, 700, None])
        self.assertEqual(w.durations(900), [900, 700, 900])

    def test_patch_writes_one_duration_per_slide(self):
        _, prs = self.deck([0, 10, 20])
        with tempfile.TemporaryDirectory() as d:
            draft, final = Path(d) / "a.pptx", Path(d) / "b.pptx"
            prs.save(draft)
            pptx_morph_patch.apply(draft, final, [900, 700, 1200], [2000, 3000, 4000])
            with ZipFile(final) as z:
                xml = [z.read(f"ppt/slides/slide{i}.xml").decode() for i in (2, 3)]
            self.assertEqual([re.search(r'p14:dur="(\d+)"', x).group(1) for x in xml], ["700", "1200"])
            self.assertEqual([re.search(r'advTm="(\d+)"', x).group(1) for x in xml], ["3000", "4000"])
            with self.assertRaises(RuntimeError):
                pptx_morph_patch.apply(draft, final, [900, 700], 2000)  # wrong length

    def test_proxy_interpolates_rotation_the_short_way(self):
        _, prs = self.deck([350, 10])
        with tempfile.TemporaryDirectory() as d:
            src, out = Path(d) / "a.pptx", Path(d) / "p.pptx"
            prs.save(src)
            pptx_morph_proxy.build(src, out, 1)
            mid = Presentation(out).slides[1]  # the single in-between frame
            rot = {s.name: s.rotation for s in mid.shapes}["!!P00_box"]
            self.assertAlmostEqual(rot % 360, 0.0, delta=0.5)  # 350 -> 10 passes through 0, not through 180


@unittest.skipIf(Presentation is None, "python-pptx not installed")
class Demo(unittest.TestCase):
    def test_demo_builds_with_matching_names_and_varied_durations(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "demo.pptx"
            demo.build(out)
            prs = Presentation(out)
            self.assertEqual(len(prs.slides), len(demo.SLIDES))
            for slide in prs.slides:
                names = [s.name for s in slide.shapes]
                self.assertEqual(len(names), len(set(names)))
            with ZipFile(out) as z:
                durs = {re.search(r'p14:dur="(\d+)"', z.read(f"ppt/slides/slide{i}.xml").decode()).group(1)
                        for i in range(2, len(demo.SLIDES) + 1)}
            self.assertGreater(len(durs), 3)


if __name__ == "__main__":
    unittest.main()
