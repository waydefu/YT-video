"""Offline checks of the brand-asset pin logic (no network). Does not prove any licence; see docs/ASSET-RIGHTS.md."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import brand_assets as B  # noqa: E402


class Pins(unittest.TestCase):
    def test_only_confirmed_vendor_is_listed(self):
        # Anthropic, Google and DeepSeek stay text-only; OpenAI and Kimi have no obtainable official file yet.
        self.assertEqual({a["vendor"] for a in B.ASSETS.values()}, {"OpenCode", "Cursor"})

    def test_every_asset_records_terms_and_hash(self):
        for name, a in B.ASSETS.items():
            self.assertEqual(len(a["sha256"]), 64, name)
            self.assertTrue(a["terms_url"].startswith("https://"), name)
            self.assertTrue(a["url"].startswith("https://"), name)
            self.assertRegex(a["accessed"], r"^\d{4}-\d{2}-\d{2}$")

    def test_verify_rejects_missing_and_modified_files(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x.png"
            self.assertFalse(B.verify(f, "0" * 64))
            f.write_bytes(b"abc")
            self.assertTrue(B.verify(f, B.sha256(f)))
            self.assertFalse(B.verify(f, "0" * 64))


if __name__ == "__main__":
    unittest.main()
