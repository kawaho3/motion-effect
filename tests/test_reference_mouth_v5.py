"""Offline regression checks for reference-style mouth articulation."""
import importlib.util
import sys
import unittest
from pathlib import Path
from PIL import Image, ImageChops
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/'episodes'/'vegetable_shop'
sys.path.insert(0,str(MODULE))
from mouth_rig import mouth_variant, MOUTHS

class ReferenceMouthTests(unittest.TestCase):
    def test_all_six_poses_exist_and_are_distinct(self):
        self.assertEqual(set(MOUTHS),{'rest','closed','soft','e','a','o','f'})
        src=Image.open(MODULE/'assets'/'Max_Standing.png').convert('RGBA')
        center=(166,149)
        crops={}
        for p in MOUTHS:
            image=mouth_variant(src,center,p)
            self.assertEqual(image.size,src.size)
            self.assertEqual(image.getchannel('A').tobytes(),src.getchannel('A').tobytes())
            crops[p]=np.asarray(image.crop((128,128,204,181)).convert('RGB'),dtype=np.int16)
        for a,b in [('closed','e'),('closed','a'),('closed','o'),('e','o'),('soft','a'),('f','a')]:
            diff=np.abs(crops[a]-crops[b]).mean()
            self.assertGreater(diff,2.0,(a,b,diff))

    def test_no_silhouette_or_nonface_changes(self):
        src=Image.open(MODULE/'assets'/'Mia_Standing.png').convert('RGBA')
        for p in MOUTHS:
            out=mouth_variant(src,(166,162),p)
            x=np.asarray(out.convert('RGBA'))
            y=np.asarray(src)
            self.assertTrue(np.array_equal(x[210:,:,:],y[210:,:,:]))
            self.assertTrue(np.array_equal(x[:110,:,:],y[:110,:,:]))

    def test_mouth_contours_drawn_in_scaled_space(self):
        """Catch old bug: polygon at 4x but lip outline at 1x appeared flat."""
        src=Image.open(MODULE/'assets'/'Mia_Standing.png').convert('RGBA')
        open_face=np.asarray(mouth_variant(src,(166,162),'a').convert('RGB'),dtype=np.int16)
        closed_face=np.asarray(mouth_variant(src,(166,162),'closed').convert('RGB'),dtype=np.int16)
        center=open_face[151:181,130:202]
        other=closed_face[151:181,130:202]
        self.assertGreater(np.abs(center-other).mean(),8.0)
        # The wide-open cavity has dark near-center pixels not present in resting smile.
        mouth=open_face[157:177,143:190]
        dark=np.mean(np.mean(mouth,axis=2)<110)
        self.assertGreater(dark,.07)

if __name__=='__main__': unittest.main()