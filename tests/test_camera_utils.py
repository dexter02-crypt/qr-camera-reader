import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock,patch
import cv2
import numpy as np
import camera_utils as u
import app

class IOTests(unittest.TestCase):
    def test_pair_export_and_read(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t).resolve()/'out.png';im=np.zeros((80,120,3),np.uint8)
            a,b=u.export_pair(im,{'ok':True},p);self.assertEqual(u.read_image(a).shape,im.shape);self.assertTrue(b.is_file())
    def test_export_never_overwrites_image(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t).resolve()/'out.png';p.write_bytes(b'original')
            with self.assertRaises(ValueError):u.export_pair(np.zeros((80,80,3),np.uint8),{},p)
            self.assertEqual(p.read_bytes(),b'original')
    def test_metadata_collision_prevents_image_write(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t).resolve()/'out.png';p.with_suffix('.json').write_text('keep')
            with self.assertRaises(ValueError):u.export_pair(np.zeros((80,80,3),np.uint8),{},p)
            self.assertFalse(p.exists())
    def test_symlink_output_refused(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();(root/'link').symlink_to(root,target_is_directory=True)
            with self.assertRaises(ValueError):u.export_pair(np.zeros((80,80,3),np.uint8),{},root/'link/out.png')
    def test_invalid_frames(self):
        for f in (None,np.zeros((10,10,3),np.uint8),np.zeros((80,80),np.uint8),np.zeros((80,80,3),float)):
            with self.assertRaises(ValueError):u.validate_frame(f)
    def test_invalid_image_data(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.png';p.write_bytes(b'not an image')
            with self.assertRaises((ValueError,cv2.error)):u.read_image(p)
    def test_network_camera_rejected_before_open(self):
        with patch.object(cv2,'VideoCapture') as cap,self.assertRaises(ValueError):
            with u.capture('https://example.invalid/video'):pass
        cap.assert_not_called()
    def test_failed_camera_releases(self):
        c=MagicMock();c.isOpened.return_value=False
        with patch.object(cv2,'VideoCapture',return_value=c),self.assertRaises(ValueError):
            with u.capture(0):pass
        c.release.assert_called_once()
    def test_processing_exception_releases_camera_and_windows(self):
        c=MagicMock();c.isOpened.return_value=True;c.read.return_value=(True,np.zeros((80,120,3),np.uint8))
        with patch.object(cv2,'VideoCapture',return_value=c),patch.object(cv2,'namedWindow'),patch.object(cv2,'destroyAllWindows') as cleanup,self.assertRaises(ValueError):
            u.camera_loop('test',lambda f,t:(_ for _ in ()).throw(ValueError('failure')))
        c.release.assert_called_once();cleanup.assert_called_once()
    def test_one_frame_loop_without_gui_or_camera(self):
        c=MagicMock();c.isOpened.return_value=True;c.read.return_value=(True,np.zeros((80,120,3),np.uint8))
        with patch.object(cv2,'VideoCapture',return_value=c),patch.object(cv2,'namedWindow'),patch.object(cv2,'imshow'),patch.object(cv2,'waitKey',return_value=-1),patch.object(cv2,'destroyAllWindows'):
            u.camera_loop('test',lambda f,t:f,max_frames=1)
        c.release.assert_called_once();c.read.assert_called_once()
    def test_header_keeps_input(self):
        f=np.zeros((80,120,3),np.uint8);a=u.header(f,['one','two']);self.assertTrue(np.all(f==0));self.assertEqual(a.shape,(170,640,3))
    def test_cli_demo_and_duplicate_output(self):
        with tempfile.TemporaryDirectory() as t,contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            p=Path(t).resolve()/'demo.png';self.assertEqual(app.main(['demo','--output',str(p)]),0)
            before=p.read_bytes();self.assertEqual(app.main(['demo','--output',str(p)]),2);self.assertEqual(p.read_bytes(),before)

if __name__=='__main__':unittest.main()
