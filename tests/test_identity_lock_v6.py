"""Hard regression: idle and speaking MUST be the same face for Max AND Mia."""
import sys
import unittest
from pathlib import Path
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parents[1]/'episodes'/'vegetable_shop'
sys.path.insert(0,str(HERE))
from identity_lock import locked_mouth_variant, MOUTHS, MOUTH_RADIUS

class IdentityLockTests(unittest.TestCase):
    def test_max_and_mia_unchanged_outside_mouth(self):
        for name,cy in [('Max',149),('Mia',162)]:
            original=Image.open(HERE/'assets'/f'{name}_Standing.png').convert('RGBA')
            source=np.array(original)
            cx=166
            mask=np.zeros(source.shape[:2],bool)
            rx,ry=MOUTH_RADIUS
            # Extra three pixels of safety margin around anti-aliased edge.
            mask[cy-ry-5:cy+ry+6,cx-rx-5:cx+rx+6]=True
            for pose in MOUTHS:
                with self.subTest(character=name,pose=pose):
                    processed=np.array(locked_mouth_variant(original,(cx,cy),pose))
                    self.assertTrue(np.array_equal(source[~mask],processed[~mask]),
                                    'Facial identity changed outside the lip edit area')
                    self.assertTrue(np.array_equal(source[:,:,3],processed[:,:,3]),
                                    'Character silhouette/alpha changed')
                    # Eye region and brows must be *exactly* identical
                    self.assertTrue(np.array_equal(source[:cy-ry-6],processed[:cy-ry-6]))

    def test_return_to_idle_is_lossless(self):
        for name,cy in [('Max',149),('Mia',162)]:
            original=Image.open(HERE/'assets'/f'{name}_Standing.png').convert('RGBA')
            for pose in ('a','e','o','f','closed','soft'):
                talking=locked_mouth_variant(original,(166,cy),pose)
                self.assertNotEqual(np.asarray(talking).tobytes(),np.asarray(original).tobytes())
                # No state is carried forward from the talking pose.
                idle=locked_mouth_variant(original,(166,cy),'rest')
                self.assertTrue(np.array_equal(np.asarray(original),np.asarray(idle)))

    def test_reject_unknown_poses(self):
        source=Image.open(HERE/'assets'/'Mia_Standing.png').convert('RGBA')
        with self.assertRaises(ValueError):
            locked_mouth_variant(source,(166,162),'a totally different face')

if __name__=='__main__': unittest.main()