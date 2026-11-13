"""Run a tiny local FFmpeg alpha codec smoke test, without any model/API calls."""
import importlib.util
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]


def import_script(name):
    spec = importlib.util.spec_from_file_location(name, root / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SyntheticMediaIntegration(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg/ffprobe unavailable')
    def test_generated_clip_and_both_alpha_formats(self):
        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            self.skipTest('Pillow unavailable')
        demo = import_script('make_demo')
        extractor = import_script('extract_character')
        verify = import_script('verify_export')
        with tempfile.TemporaryDirectory() as t:
            folder = Path(t)
            source, reference = demo.make_demo(folder, frames=8, width=240, height=320, fps=8)
            self.assertTrue(source.is_file())
            self.assertTrue(verify.check_file(reference, include_hash=False)['passes_sampled_export_checks'])
            for extension in ('.webm', '.mov'):
                output = folder / f'encoded{extension}'
                cmd = extractor.encode_command(folder / 'ground_truth_rgba/frame_%06d.png', output, '8/1')
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
                report = verify.check_file(output, include_hash=False)
                self.assertTrue(report['passes_sampled_export_checks'], extension)
                self.assertEqual(report['audio_streams'], 0)
                self.assertEqual((report['width'], report['height']), (240, 320))


if __name__ == '__main__':
    unittest.main()