"""Test OOXML insertion, matching object names, Fallback, and ZIP media dedup."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("pptx_morph_patch", ROOT / "scripts/pptx_morph_patch.py")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SLIDE = '''<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
 <p:cSld><p:spTree>
  <p:sp><p:nvSpPr><p:cNvPr id="2" name="Text 1" descr="!!TITLE"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr></p:sp>
 </p:spTree></p:cSld>
 <p:clrMapOvr/>
</p:sld>'''
def fixture(path):
    with ZipFile(path, "w") as z:
        for i in (1, 2, 3):
            z.writestr(f"ppt/slides/slide{i}.xml", SLIDE)
            z.writestr(f"ppt/slides/_rels/slide{i}.xml.rels",
                '<Relationships><Relationship Target="../media/image'+str(i)+'.png"/></Relationships>')
            z.writestr(f"ppt/media/image{i}.png", b"same_image_bytes")

class MorphPatchTests(unittest.TestCase):
    def test_morph_fallback_and_names(self):
        with TemporaryDirectory() as d:
            src=Path(d)/"before.pptx"
            dst=Path(d)/"after.pptx"
            fixture(src)
            count, dedup=MODULE.apply(src,dst,1300,4700,True)
            self.assertEqual((count,dedup),(3,2))
            with ZipFile(dst) as z:
                for i in (1,2,3):
                    xml=z.read(f"ppt/slides/slide{i}.xml").decode()
                    ET.fromstring(xml)
                    self.assertIn('name="!!TITLE"',xml)
                    self.assertIn('advTm="4700"',xml)
                    if i>1:
                        self.assertIn('<p159:morph option="byObject"/>',xml)
                        self.assertIn('<mc:Fallback>',xml)
                        self.assertIn('p14:dur="1300"',xml)
                    else:
                        self.assertNotIn('<p159:morph',xml)
                media=[x for x in z.namelist() if x.startswith("ppt/media/")]
                self.assertEqual(len(media),1)

if __name__=="__main__":
    unittest.main()
