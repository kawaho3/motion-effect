"""No network / model weights required: deterministic 12-stop + face-timing QA."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EP=ROOT/'episodes'/'vegetable_shop'
sys.path.insert(0,str(EP))
import journey
import journey_backgrounds as scenery

class JourneyTests(unittest.TestCase):
    def test_exactly_twelve_ten_second_places(self):
        self.assertEqual(journey.DURATION,120)
        self.assertEqual(journey.FPS,30)
        self.assertEqual(journey.SCENE_SECONDS,10)
        self.assertEqual(len(scenery.STOPS),12)
        self.assertEqual(len(set(x[0] for x in scenery.STOPS)),12)

    def test_phones_to_six_visemes(self):
        self.assertEqual(journey.phoneme_pose('m'),'closed')
        self.assertEqual(journey.phoneme_pose('ɑ'),'a')
        self.assertEqual(journey.phoneme_pose('u'),'o')
        self.assertEqual(journey.phoneme_pose('e'),'e')
        self.assertEqual(journey.phoneme_pose('t'),'soft')
        self.assertEqual(journey.phoneme_pose('ː'),'rest')

    def test_exclusive_timeline(self):
        frames=journey.build_controls([{'speaker':'Max','start':1,'end':2,
           'phones':[{'phone':'ɑ','start':1.1,'end':1.5}], 'joke':True}],30,3)
        self.assertEqual(len(frames[0]['Max']),90)
        self.assertEqual(frames[0]['Max'][40],'a')
        self.assertEqual(frames[0]['Mia'][40],'rest')
        self.assertTrue(frames[2]['Max'][40])

    def test_twelve_backdrops_are_different(self):
        hashes=[]
        for n in range(12):
            im=scenery.render_background(n,64,36)
            self.assertEqual(im.size,(64,36))
            hashes.append(hash(im.tobytes()))
        self.assertEqual(len(set(hashes)),12)

    def test_transparent_character_assets_exist(self):
        for who in ('Max','Mia'):
            im=journey._rgba_source(who)
            self.assertGreater(im.width,200)
            self.assertGreater(im.height,800)
            self.assertLess(im.getchannel('A').getextrema()[0],255)

if __name__=='__main__':unittest.main()