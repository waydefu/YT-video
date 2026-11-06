import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ProductionContractTests(unittest.TestCase):
    def test_scene_script_syntax(self):
        source = (ROOT / "blender/scene.py").read_text()
        ast.parse(source)
        self.assertIn('volume_smoke()', source)
        self.assertIn('spotlight("01 - LEFT sequential beam"', source)
        self.assertIn('spotlight("02 - RIGHT sequential beam"', source)
        self.assertIn("shatter_and_reform", source)
        self.assertIn("camera_text(", source)

    def test_media_script_syntax(self):
        for name in ("soundtrack.py", "validate_media.py"):
            ast.parse((ROOT / "scripts" / name).read_text())

    def test_format_and_safe_zone(self):
        cfg = json.loads((ROOT / "config/production.json").read_text())
        f = cfg["format"]
        self.assertEqual((f["width"], f["height"], f["fps"]), (1920, 1080, 24))
        self.assertEqual(f["width"] * 9, f["height"] * 16)
        a = cfg["safe_area"]["titles"]
        self.assertGreaterEqual(a["left"], .15)
        self.assertLessEqual(a["right"], .85)
        self.assertGreaterEqual(a["top"], .15)
        self.assertLessEqual(a["bottom"], .85)

    def test_nonoverlap(self):
        cfg = json.loads((ROOT / "config/production.json").read_text())
        self.assertLess(cfg["lights"]["left"]["end"], cfg["lights"]["right"]["start"])
        self.assertLess(cfg["lights"]["right"]["end"], cfg["emergence_start"])
        self.assertLess(cfg["emergence_start"], cfg["fracture_start"])
        self.assertLess(cfg["fracture_start"], cfg["reassemble_start"])
        self.assertLess(cfg["reassemble_start"], cfg["title_start"])

if __name__ == "__main__":
    unittest.main()
