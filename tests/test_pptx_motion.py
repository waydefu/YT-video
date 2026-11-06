"""Structure tests for the autoplay idle-motion layer and the layer-A validator.

These prove OOXML structure only. They do NOT prove Microsoft PowerPoint playback.
"""
import json
import subprocess
import sys
import unittest
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    mod = module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


MOTION = load("pptx_motion")
MORPH = load("pptx_morph_patch")
VALIDATE = load("pptx_validate")

NS = ('xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
      'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"')


def shape(i, name, text=False, rot=None):
    body = '<p:txBody><a:bodyPr/><a:p><a:r><a:t>Hi</a:t></a:r></a:p></p:txBody>' if text else ""
    r = f' rot="{rot}"' if rot is not None else ""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{i}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm{r}><a:off x="914400" y="914400"/><a:ext cx="914400" cy="914400"/>'
            f'</a:xfrm></p:spPr>{body}</p:sp>')


def slide_xml():
    shapes = shape(2, "!!HEAD") + shape(3, "!!EYE") + shape(4, "!!TITLE", text=True) + shape(5, "!!BG")
    return (f'<?xml version="1.0" encoding="UTF-8"?><p:sld {NS}><p:cSld><p:spTree>'
            f"{shapes}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>")


def deck(path, slides=2):
    with ZipFile(path, "w") as z:
        z.writestr("ppt/presentation.xml",
                   f'<p:presentation {NS}><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
        for i in range(1, slides + 1):
            z.writestr(f"ppt/slides/slide{i}.xml", slide_xml())


SPEC = {"slides": {"1": [
    {"target": "!!HEAD", "effect": "sway", "degrees": 2, "period_ms": 3200},
    {"target": "!!EYE", "effect": "blink", "period_ms": 4800, "close_ms": 80},
    {"target": "!!TITLE", "effect": "breathe", "period_ms": 2400},
    {"target": "!!BG", "effect": "orbit", "period_ms": 6400},
    {"target": "!!BG", "effect": "spin", "period_ms": 24000},
    {"target": "!!HEAD", "effect": "float", "dy_in": 0.05, "period_ms": 1600},
]}}


class MotionTests(unittest.TestCase):
    def build(self, d, spec=SPEC):
        src, dst = Path(d) / "a.pptx", Path(d) / "b.pptx"
        deck(src)
        report = MOTION.apply(src, dst, spec)
        with ZipFile(dst) as z:
            xml = z.read("ppt/slides/slide1.xml").decode()
        return xml, report

    def test_timing_is_wellformed_and_autostarts(self):
        with TemporaryDirectory() as d:
            xml, report = self.build(d)
            root = ET.fromstring(xml)
            ns = {"p": MOTION.P}
            self.assertIn('<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond>', xml)
            rows = [c for c in root.iter(f"{{{MOTION.P}}}cTn") if c.get("presetClass")]
            self.assertEqual(len(rows), 6)
            self.assertTrue(all(r.get("repeatCount") == "indefinite" for r in rows))
            self.assertEqual(rows[0].get("nodeType"), "afterEffect")
            self.assertTrue(all(r.get("nodeType") == "withEffect" for r in rows[1:]))
            ids = [c.get("id") for c in root.iter(f"{{{MOTION.P}}}cTn")]
            self.assertEqual(len(ids), len(set(ids)))
            targets = {t.get("spid") for t in root.iter(f"{{{MOTION.P}}}spTgt")}
            self.assertEqual(targets, {"2", "3", "4", "5"})
            self.assertEqual(len(report[1]), 6)
            self.assertIsNotNone(root.find("p:timing", ns))

    def test_grpid_unique_per_shape_and_bldp_only_for_text_shapes(self):
        with TemporaryDirectory() as d:
            xml, _ = self.build(d)
            root = ET.fromstring(xml)
            pairs = [(r.find(".//{%s}spTgt" % MOTION.P).get("spid"), r.get("grpId"))
                     for r in root.iter(f"{{{MOTION.P}}}cTn") if r.get("presetClass")]
            self.assertEqual(len(pairs), len(set(pairs)))
            builds = [(b.get("spid"), b.get("grpId")) for b in root.iter(f"{{{MOTION.P}}}bldP")]
            self.assertEqual(builds, [("4", "0")])

    def test_sway_is_pre_rotated_for_symmetric_motion(self):
        with TemporaryDirectory() as d:
            xml, _ = self.build(d)
            self.assertIn('rot="-120000"', xml)  # -2 degrees
            self.assertIn('by="240000"', xml)    # +4 degree swing, autoReverse

    def test_blink_gap_math_and_orbit_path(self):
        with TemporaryDirectory() as d:
            xml, _ = self.build(d)
            self.assertIn('<p:cond delay="4640"/>', xml)      # 4800 - 2*80
            self.assertIn('autoRev="1"', xml)
            self.assertIn('path="M 0 0 C ', xml)
            self.assertIn(" Z\"", xml)
            self.assertIn('path="M 0 0 L 0 0.00667 E"', xml)  # 0.05in / 7.5in

    def test_errors(self):
        with TemporaryDirectory() as d:
            for bad in (
                {"slides": {"1": [{"target": "!!NOPE", "effect": "spin"}]}},
                {"slides": {"1": [{"target": "!!HEAD", "effect": "wobble"}]}},
                {"slides": {"1": [{"target": "!!HEAD", "effect": "spin", "bogus": 1}]}},
                {"slides": {"1": [{"target": "!!EYE", "effect": "blink", "period_ms": 200, "close_ms": 80}]}},
                {"slides": {"9": [{"target": "!!HEAD", "effect": "spin"}]}},
            ):
                with self.assertRaises(MOTION.MotionError):
                    self.build(d, bad)

    def test_refuses_to_overwrite_existing_timing(self):
        with TemporaryDirectory() as d:
            xml, _ = self.build(d)
            with self.assertRaises(MOTION.MotionError):
                MOTION.apply_to_slide(xml, (13.333, 7.5), SPEC["slides"]["1"])

    def test_morph_then_motion_keeps_schema_order_and_validates(self):
        with TemporaryDirectory() as d:
            a, b, c = (Path(d) / n for n in ("a.pptx", "b.pptx", "c.pptx"))
            deck(a)
            MORPH.apply(a, b, 1400, 4800, False)
            spec = {"slides": {"1": SPEC["slides"]["1"], "2": SPEC["slides"]["1"]}}
            MOTION.apply(b, c, spec)
            with ZipFile(c) as z:
                for i in (1, 2):
                    root = ET.fromstring(z.read(f"ppt/slides/slide{i}.xml"))
                    kids = [k.tag.rsplit("}", 1)[-1] for k in root]
                    self.assertIn(kids, (["cSld", "clrMapOvr", "transition", "timing"],
                                         ["cSld", "clrMapOvr", "AlternateContent", "timing"]))

            class Args:
                min_loops, hold_ms, edge, min_font, spin_symmetry_deg = 3, 4800, 0.05, 14, 0
            rep = VALIDATE.validate(c, Args)
            self.assertEqual(rep["fails"], [], rep["fails"])
            self.assertEqual(rep["loops"], {1: 6, 2: 6})
            self.assertEqual(rep["morph"], 1)
            # 24000 ms spin does not divide a 4800 ms hold -> flagged? 4800 % 24000 != 0
            self.assertTrue(any("do not divide hold" in w for w in rep["warns"]))
            # 24000 ms spin = 360 deg; per 4800 ms hold that is 72 deg = not a multiple of 45 deg
            Args.spin_symmetry_deg = 72.0  # symmetric art repeating every 72 deg is identical at each cut
            rep2 = VALIDATE.validate(c, Args)
            self.assertFalse(any("24000" in w for w in rep2["warns"]), rep2["warns"])

    def test_validator_flags_misordered_and_dead_slides(self):
        with TemporaryDirectory() as d:
            a, b = Path(d) / "a.pptx", Path(d) / "b.pptx"
            deck(a)

            class Args:
                min_loops, hold_ms, edge, min_font, spin_symmetry_deg = 3, 0, 0.05, 14, 0
            rep = VALIDATE.validate(a, Args)
            self.assertEqual(rep["dead"], [1, 2])
            self.assertTrue(any("no p159:morph" in f for f in rep["fails"]))
            cli = subprocess.run([sys.executable, str(ROOT / "scripts/pptx_validate.py"), str(a)],
                                 capture_output=True, text=True)
            self.assertEqual(cli.returncode, 1)
            self.assertIn("FAIL", cli.stdout)


class ReadabilityTests(unittest.TestCase):
    def test_small_text_is_flagged(self):
        with TemporaryDirectory() as d:
            path = Path(d) / "a.pptx"
            deck(path, slides=1)
            with ZipFile(path) as z:
                parts = {n: z.read(n) for n in z.namelist()}
            xml = parts["ppt/slides/slide1.xml"].decode()
            xml = xml.replace("<a:r><a:t>Hi</a:t></a:r>", '<a:r><a:rPr sz="1000"/><a:t>Tiny</a:t></a:r>')
            parts["ppt/slides/slide1.xml"] = xml.encode()
            with ZipFile(path, "w") as z:
                for n, b in parts.items():
                    z.writestr(n, b)

            class Args:
                min_loops, hold_ms, edge, min_font, spin_symmetry_deg = 0, 0, 0.05, 14, 0
            rep = VALIDATE.validate(path, Args)
            self.assertTrue(any("'Tiny' is 10 pt" in w for w in rep["warns"]), rep["warns"])


if __name__ == "__main__":
    unittest.main()
