"""Baseline command-formation tests. No network or paid model needed."""
import importlib.util
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('extract_character', root / 'scripts' / 'extract_character.py')
extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extractor)


class EncoderTests(unittest.TestCase):
    def test_webm_has_alpha_and_no_audio(self):
        args = extractor.encode_command('frames/frame_%06d.png', Path('out.webm'), '25/1')
        self.assertIn('yuva420p', args)
        self.assertIn('libvpx-vp9', args)
        self.assertIn('-an', args)
        self.assertIn('-auto-alt-ref', args)

    def test_mov_matches_historical_prores_format(self):
        args = extractor.encode_command('frames/frame_%06d.png', Path('out.mov'), '25/1')
        self.assertIn('prores_ks', args)
        self.assertIn('yuva444p10le', args)
        self.assertIn('-an', args)

    def test_mov_qtrle_alternative(self):
        args = extractor.encode_command('f_%06d.png', Path('o.mov'), '30', mov_codec='qtrle')
        self.assertIn('argb', args)
        self.assertIn('qtrle', args)

    def test_unsupported_extension(self):
        with self.assertRaises(ValueError):
            extractor.encode_command('f_%06d.png', Path('o.mp4'), '25')

    def test_bad_mov_codec(self):
        with self.assertRaises(ValueError):
            extractor.encode_command('f_%06d.png', Path('o.mov'), '25', mov_codec='h264')


if __name__ == '__main__':
    unittest.main()