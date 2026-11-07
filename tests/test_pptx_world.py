"""Geometry and naming tests for the panel/camera world used by the seamless-transition decks.

Layer A only: they prove the placement math and name hygiene, not how PowerPoint plays the Morph.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from pptx import Presentation
    from pptx.util import Emu
except ImportError:  # pragma: no cover - python-pptx is optional for the stdlib-only test run
    Presentation = None

if Presentation is not None:
    import pptx_world
    from pptx_world import H, W, World

WIN = 3.9


def noop(ctx):
    return None


@unittest.skipIf(Presentation is None, "python-pptx not installed")
class WorldGeometry(unittest.TestCase):
    def make(self):
        w = World(gap=0.6)
        w.first(noop)
        w.add(noop, "zoom_in", window=(0.9, 4.8, WIN))
        w.add(noop, "pull_back", frame=(0.9, 2.1, WIN))
        w.add(noop, "pan_right")
        w.add(noop, "pan_down")
        return w

    def test_zoom_in_nests_the_next_panel_inside_the_window(self):
        w = self.make()
        a, b = w.panels[0], w.panels[1]
        self.assertAlmostEqual(b.s, WIN / W)
        self.assertAlmostEqual(b.ox, a.ox + 0.9)
        self.assertAlmostEqual(b.oy, a.oy + 4.8)
        self.assertAlmostEqual(b.rect[2] - b.rect[0], WIN)  # world width equals the window width

    def test_pull_back_hangs_the_previous_panel_in_the_frame_and_restores_scale(self):
        w = self.make()
        prev, big = w.panels[1], w.panels[2]
        self.assertAlmostEqual(big.s, 1.0)  # window width == frame width, so the scale returns to 1
        self.assertAlmostEqual(big.ox + 0.9 * big.s, prev.ox)
        self.assertAlmostEqual(big.oy + 2.1 * big.s, prev.oy)
        self.assertAlmostEqual((prev.rect[2] - prev.rect[0]), WIN * big.s)
        self.assertLess(big.rank, prev.rank)  # drawn beneath the picture it contains
        self.assertGreater(big.rank, w.panels[0].rank)  # but above the page it overlaps

    def test_pans_keep_scale_and_leave_a_gap(self):
        w = self.make()
        big, right, down = w.panels[2], w.panels[3], w.panels[4]
        self.assertAlmostEqual(right.ox, big.ox + W + 0.6)
        self.assertAlmostEqual(right.oy, big.oy)
        self.assertAlmostEqual(down.oy, right.oy + H + 0.6)
        self.assertAlmostEqual(down.s, right.s)

    def test_camera_zoom_is_inverse_scale(self):
        w = self.make()
        for i, p in enumerate(w.panels):
            cx, cy, z = w.view(i)
            self.assertAlmostEqual(z, 1 / p.s)
            self.assertAlmostEqual(cx, p.ox + W * p.s / 2)

    def test_pull_back_scene_exists_only_from_its_own_slide(self):
        w = self.make()
        ids = lambda j: [p.idx for p in w._visible(j)]  # noqa: E731
        self.assertNotIn(2, ids(0))
        self.assertNotIn(2, ids(1))
        self.assertIn(2, ids(2))


@unittest.skipIf(Presentation is None, "python-pptx not installed")
class WorldDrawing(unittest.TestCase):
    def test_names_are_unique_prefixed_and_text_reads_at_design_size(self):
        def draw(ctx):
            ctx.rect("card", 0, 0, W, H, "FFFFFF")
            ctx.text("t", "標題", 0.9, 1.0, 6.0, 0.8, 40, "000000", "Noto Sans CJK TC", "Noto Sans CJK TC")

        w = World(gap=0.6)
        w.first(draw)
        w.add(draw, "zoom_in", window=(0.9, 4.8, WIN))
        w.add(draw, "pull_back", frame=(0.9, 2.1, WIN))
        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(int(W * 914400)), Emu(int(H * 914400))
        readable = w.build(prs)
        self.assertEqual(len(prs.slides), 3)
        for slide in prs.slides:
            names = [s.name for s in slide.shapes]
            self.assertEqual(len(names), len(set(names)))
            self.assertTrue(all(n.startswith("!!P") for n in names))
        # on slide 2 the focused panel (index 1) is zoomed 1/s, so its 40 pt title reads at 40 pt
        sizes = {s.name: s.text_frame.paragraphs[0].runs[0].font.size.pt for s in prs.slides[1].shapes if s.has_text_frame and s.text_frame.text}
        self.assertAlmostEqual(sizes["!!P01_t"], 40.0, places=1)
        self.assertLess(sizes["!!P00_t"], 100.0 * 40 / 40 + 1e-6 + 200)  # sanity: the big parent is scaled up, not exploded
        self.assertEqual(readable["2"], ["!!P01_t"])

    def test_oversized_shapes_are_rejected(self):
        def draw(ctx):
            ctx.rect("huge", 0, 0, 300, 5, "FFFFFF")

        w = World()
        w.first(draw)
        with self.assertRaises(ValueError):
            w.build(Presentation())


@unittest.skipIf(Presentation is None, "python-pptx not installed")
class BoardMode(unittest.TestCase):
    """nest(parent) + zoom_out(to): a hub with sibling windows that the camera pans between, then returns to."""

    def make(self):
        w = World(gap=0.6)
        w.first(noop)
        w.add(noop, "nest", window=(0.9, 2.2, 3.6), parent=0)
        w.add(noop, "nest", window=(4.95, 2.2, 3.6), parent=0)
        w.add(noop, "zoom_out", to=0)
        return w

    def test_siblings_share_scale_and_are_nested_in_the_hub(self):
        w = self.make()
        hub, a, b = w.panels[0], w.panels[1], w.panels[2]
        self.assertAlmostEqual(a.s, 3.6 / W)
        self.assertAlmostEqual(a.s, b.s)  # panning between them is a plain pan: no zoom change
        self.assertAlmostEqual(b.ox - a.ox, 4.05)
        self.assertAlmostEqual(a.oy, hub.oy + 2.2)
        self.assertAlmostEqual(w.view(2)[2] / w.view(1)[2], 1.0)

    def test_zoom_out_revisits_the_hub_with_the_same_names_and_replaces_it(self):
        w = self.make()
        hub, back = w.panels[0], w.panels[3]
        self.assertEqual((back.ox, back.oy, back.s), (hub.ox, hub.oy, hub.s))
        self.assertEqual(back.name_idx, hub.name_idx)  # same `!!` names, so Morph continues the same objects
        ids = lambda j: [p.idx for p in w._visible(j)]  # noqa: E731
        self.assertIn(0, ids(2))
        self.assertNotIn(3, ids(2))  # the revisit exists only from its own slide on
        self.assertIn(3, ids(3))
        self.assertNotIn(0, ids(3))  # and it replaces the original: each object is drawn once

    def test_every_slide_has_unique_names_and_the_hub_keeps_its_names(self):
        def hub(ctx):
            ctx.rect("card", 0, 0, W, H, "FFFFFF")

        def child(ctx):
            ctx.rect("card", 0, 0, W, H, "EEEEEE")

        w = World(gap=0.6)
        w.first(hub)
        w.add(child, "nest", window=(0.9, 2.2, 3.6), parent=0)
        w.add(hub, "zoom_out", to=0)
        prs = Presentation()
        prs.slide_width, prs.slide_height = Emu(int(W * 914400)), Emu(int(H * 914400))
        w.build(prs)
        per_slide = [[s.name for s in sl.shapes] for sl in prs.slides]
        for names in per_slide:
            self.assertEqual(len(names), len(set(names)))
        self.assertIn("!!P00_card", per_slide[0])
        self.assertIn("!!P00_card", per_slide[2])  # the revisited hub reuses the original names
        self.assertNotIn("!!P02_card", per_slide[2])


if __name__ == "__main__":
    unittest.main()
