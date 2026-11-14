"""Regression: visible lip articulation, correct speaker and close-up shots."""
import sys
import unittest
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/'episodes'/'vegetable_shop'
sys.path.insert(0,str(EP))
import journey
from mouth_rig import mouth_variant

class MouthRigTests(unittest.TestCase):
    def test_phoneme_groups_are_distinct(self):
        cases={'m':'closed','b':'closed','p':'closed','a':'a','ɑ':'a','e':'e','o':'o','u':'o','f':'f','v':'f','t':'soft'}
        for ph,expected in cases.items():
            self.assertEqual(journey.phoneme_pose(ph),expected)

    def test_mouth_visemes_change_real_pixels(self):
        for who in ('Max','Mia'):
            source=journey._rgba_source(who)
            cx,cy=journey.FACES[who]['mouth']
            crop=(cx-35,cy-17,cx+36,cy+18)
            bases=[]
            for name in ('rest','closed','e','a','o','f'):
                img=mouth_variant(source,(cx,cy),name)
                self.assertEqual(img.size,source.size)
                self.assertEqual(img.getchannel('A').tobytes(),source.getchannel('A').tobytes())
                bases.append(np.asarray(img.crop(crop).convert('RGB')))
            for i in range(1,len(bases)):
                self.assertGreater(float(np.mean(np.abs(bases[i].astype(float)-bases[0].astype(float)))),2.0)
            self.assertGreater(len(set(b.tobytes() for b in bases)),5)

    def test_conversational_camera_is_active(self):
        timeline=[{'speaker':'Max','start':1,'end':4},{'speaker':'Mia','start':4.1,'end':8}]
        self.assertEqual(journey.camera_shot(.1,timeline),'wide')
        self.assertEqual(journey.camera_shot(2.1,timeline),'Max')
        self.assertEqual(journey.camera_shot(5.1,timeline),'Mia')
        self.assertEqual(journey.camera_shot(8.9,timeline),'wide')

if __name__=='__main__':unittest.main()