from pathlib import Path
import unittest
from unittest.mock import patch
import cv2
import numpy as np
from core import detect,annotate,escaped,Session
from camera_utils import read_image

class QRTests(unittest.TestCase):
    def fixture(self):return read_image(Path(__file__).resolve().parents[1]/'examples/two-codes.png')
    def test_actual_two_codes_decode(self):
        rows=detect(self.fixture());self.assertEqual({r['text'] for r in rows},{'KEDBYTE-DEMO-ONE','https://example.invalid/not-opened'});self.assertTrue(all(not r['truncated'] for r in rows))
    def test_blank_no_code(self):self.assertEqual(detect(np.full((400,600,3),255,np.uint8)),[])
    def test_input_unchanged(self):
        f=self.fixture();before=f.copy();r=detect(f);annotate(f,r);self.assertTrue(np.array_equal(f,before))
    def test_repeat_payloads_not_double_counted(self):
        s=Session();r=detect(self.fixture());self.assertEqual(s.update(r),2);self.assertEqual(s.update(r),2)
    def test_session_bounded_and_reset(self):
        s=Session();s.update([{'text':str(i),'truncated':False} for i in range(600)])
        self.assertEqual(len(s.seen),512);self.assertTrue(s.limit_reached);s.reset();self.assertEqual(len(s.seen),0)
    def test_truncated_prefix_not_counted(self):
        s=Session();self.assertEqual(s.update([{'text':'a','truncated':True}]),0)
    def test_escape_controls_and_unicode(self):
        text=escaped('\x1b[2J\nhello\t\u2603');self.assertNotIn('\x1b',text);self.assertNotIn('\n',text);self.assertIn('\\n',text);self.assertEqual(len(escaped('x'*200)),120)
    def test_partial_undecoded_results_ignored(self):
        with patch.object(cv2,'QRCodeDetector') as factory:
            factory.return_value.detectAndDecodeMulti.return_value=(True,('',),np.array([[[1,1],[50,1],[50,50],[1,50]]]),[])
            self.assertEqual(detect(np.zeros((100,100,3),np.uint8)),[])
    def test_bad_corner_results_rejected(self):
        for x in (-1,101,float('nan')):
            with patch.object(cv2,'QRCodeDetector') as factory:
                factory.return_value.detectAndDecodeMulti.return_value=(True,('x',),np.array([[[x,1],[50,1],[50,50],[1,50]]]),[])
                self.assertEqual(detect(np.zeros((100,100,3),np.uint8)),[])
    def test_long_payload_explicitly_truncated(self):
        with patch.object(cv2,'QRCodeDetector') as factory:
            factory.return_value.detectAndDecodeMulti.return_value=(True,('a'*3000,),np.array([[[1,1],[50,1],[50,50],[1,50]]]),[])
            r=detect(np.zeros((100,100,3),np.uint8))[0];self.assertEqual(len(r['text']),2048);self.assertTrue(r['truncated'])
if __name__=='__main__':unittest.main()
