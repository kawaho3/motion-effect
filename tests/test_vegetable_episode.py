"""Audio timeline and render safety checks without downloading AI model weights."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
script = ROOT / 'episodes' / 'vegetable_shop' / 'build.py'
spec = importlib.util.spec_from_file_location('vegetable_shop', script)
veg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(veg)


class VegetableEpisodeTests(unittest.TestCase):
    def test_script_and_character_names(self):
        data = veg.load_script()
        self.assertEqual(len(data), 44)
        self.assertEqual({r['speaker'] for r in data}, {'Max', 'Mia'})
        self.assertTrue(any(r['joke'] for r in data))

    def test_neural_viseme_mapping(self):
        for phone, expected in [('m','rest'),('b','rest'),('p','rest'),('a','ah'),('o','oh'),('ʊ','oh'),('s','soft'),(' ','rest')]:
            self.assertEqual(veg.phone_to_pose(phone), expected)

    def test_timing_budget(self):
        starts, gap = veg.plan_timing([2.3]*44)
        self.assertGreaterEqual(gap, .22)
        self.assertLess(starts[-1] + 2.3, 120)
        self.assertTrue(all(a < b for a,b in zip(starts,starts[1:])))

    def test_rejects_overlong_audio(self):
        with self.assertRaisesRegex(ValueError, 'too long'):
            veg.plan_timing([5.0]*44)

    def test_rejects_underlong_episode(self):
        with self.assertRaisesRegex(ValueError, 'Too little'):
            veg.plan_timing([1.0]*44)

    def test_subtitles(self):
        with tempfile.TemporaryDirectory() as root:
            filename = Path(root) / 'test.srt'
            veg.write_srt([{'start':.45,'end':2.4,'speaker':'Mia','text':'Carrots!'}], filename)
            content = filename.read_text()
            self.assertIn('00:00:00,450 --> 00:00:02,400',content)
            self.assertIn('Mia: Carrots!',content)

    def test_expression_art_gate(self):
        required = [veg.ASSETS / name for name in ('Scene_Base.png', 'Scene_Ah_Blink.png', 'Scene_Oh.png')]
        if all(p.is_file() for p in required):
            self.assertEqual(len(veg.require_expression_plates()), 3)
        else:
            with self.assertRaises(FileNotFoundError):
                veg.require_expression_plates()

if __name__ == '__main__':
    unittest.main()