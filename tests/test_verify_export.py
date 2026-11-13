"""Test verifying offline alpha export. Small fixture generated in test temp dir."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('verify_export', root / 'scripts' / 'verify_export.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class InspectorTests(unittest.TestCase):
    def test_sha256_file(self):
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'hello.txt'
            path.write_text('hello', encoding='utf8')
            self.assertEqual(verifier.sha256(path), hashlib.sha256(b'hello').hexdigest())


if __name__ == '__main__':
    unittest.main()