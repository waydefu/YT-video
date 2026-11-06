import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCENE = ROOT / "blender/v4_opening.py"
FETCH = ROOT / "scripts/fetch_cc0_bust.py"

class V4ContractTests(unittest.TestCase):
    def test_python_syntax(self):
        ast.parse(SCENE.read_text())
        ast.parse(FETCH.read_text())

    def test_actual_imported_3d_asset_not_primitive_face(self):
        source = SCENE.read_text()
        self.assertIn("bpy.ops.import_scene.gltf", source)
        self.assertNotIn("def bust(", source)
        self.assertIn("if not meshes:", source)
        self.assertIn('obj.hide_render', source)

    def test_no_horizon_and_true_volume(self):
        source = SCENE.read_text()
        self.assertIn("ShaderNodeVolumePrincipled", source)
        self.assertNotIn("primitive_plane_add", source)
        self.assertIn('scene.render.resolution_x=1920', source)
        self.assertIn('scene.render.resolution_y=1080', source)
        self.assertIn('scene.render.pixel_aspect_x=1', source)

    def test_license_origin(self):
        source = FETCH.read_text()
        self.assertIn("polyhaven.com/a/marble_bust_01", source)
        self.assertIn('magic != b"glTF"', source)
        self.assertIn("hashlib.sha256", source)
        self.assertIn("files.innerscene.com", source)

if __name__ == "__main__":
    unittest.main()
