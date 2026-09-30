"""Bounded local images, explicit exports and a camera loop with deterministic cleanup."""
from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path
import json
import math
import os
import time
import uuid
import cv2
import numpy as np


def validate_frame(frame):
    if not isinstance(frame,np.ndarray) or frame.dtype!=np.uint8 or frame.ndim!=3 or frame.shape[2]!=3:
        raise ValueError('Expected a uint8 BGR image.')
    if not (16<=frame.shape[0]<=6000 and 16<=frame.shape[1]<=6000) or frame.shape[0]*frame.shape[1]>20_000_000:
        raise ValueError('Image must be at least 16x16 and at most 20 million pixels / 6000 per side.')


def integer(value,name,low,high):
    if isinstance(value,bool) or not isinstance(value,int) or not low<=value<=high:
        raise ValueError(f'{name} must be an integer from {low} to {high}.')
    return value


def finite(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number.')
    return float(value)


def read_image(path):
    path=Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size>12_000_000:
        raise ValueError('Use a regular local image file no larger than 12 MB.')
    data=np.frombuffer(path.read_bytes(),np.uint8)
    image=cv2.imdecode(data,cv2.IMREAD_COLOR)
    validate_frame(image)
    return image


def safe_output(path):
    path=Path(path).absolute()
    if any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('Refusing symbolic links in output paths.')
    if path.exists():raise ValueError(f'Output already exists: {path.name}')
    return path


def export_pair(image,data,output=None):
    """Save only when explicitly called by demo/image commands. Never overwrite."""
    validate_frame(image)
    path=Path(output) if output else Path(__file__).resolve().parent/'outputs'/('demo-'+uuid.uuid4().hex[:12]+'.png')
    if path.suffix.lower()!='.png':raise ValueError('--output must end in .png')
    path=safe_output(path);meta=safe_output(path.with_suffix('.json'))
    ok,png=cv2.imencode('.png',image)
    if not ok:raise ValueError('Could not encode output.')
    encoded=json.dumps(data,ensure_ascii=True,allow_nan=False,indent=2).encode()+b'\n'
    if len(encoded)>2_000_000:raise ValueError('Output metadata exceeds limit.')
    path.parent.mkdir(parents=True,exist_ok=True)
    created=[]
    try:
        for target,content in ((path,png.tobytes()),(meta,encoded)):
            fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
            created.append(target)
            with os.fdopen(fd,'wb') as f:f.write(content)
    except BaseException:
        for target in created:
            if target.is_file() and not target.is_symlink():target.unlink()
        raise
    return path,meta


def header(image,lines):
    validate_frame(image)
    w=max(640,image.shape[1]);h=30*(len(lines)+1)
    strip=np.full((h,w,3),24,np.uint8)
    for i,line in enumerate(lines):
        text=''.join(c if 32<=ord(c)<127 else '?' for c in str(line))[:160]
        cv2.putText(strip,text,(12,26+30*i),cv2.FONT_HERSHEY_SIMPLEX,.48,(235,235,235),1,cv2.LINE_AA)
    bottom=np.zeros((image.shape[0],w,3),np.uint8);bottom[:,:image.shape[1]]=image
    return np.vstack((strip,bottom))


@contextmanager
def capture(index):
    integer(index,'camera',0,16)
    cap=cv2.VideoCapture(index)
    try:
        if not cap.isOpened():raise ValueError('Cannot open camera. Close other camera apps and check Terminal camera permission.')
        yield cap
    finally:cap.release()


def camera_loop(title,process,*,camera=0,on_click=None,on_key=None,max_frames=None):
    integer(camera,'camera',0,16)
    if max_frames is not None:integer(max_frames,'max-frames',1,1000000)
    latest={'frame':None,'offset':0}
    def mouse(event,x,y,flags,param):
        frame=latest['frame'];yy=y-latest['offset']
        if on_click and event==cv2.EVENT_LBUTTONDOWN and frame is not None and 0<=x<frame.shape[1] and 0<=yy<frame.shape[0]:
            on_click(frame,x,yy)
    try:
        with capture(camera) as cap:
            cv2.namedWindow(title,cv2.WINDOW_AUTOSIZE)
            if on_click:cv2.setMouseCallback(title,mouse)
            count=0
            while True:
                ok,frame=cap.read()
                if not ok:raise ValueError('Camera stopped returning frames.')
                validate_frame(frame)
                if frame.shape[1]>960:frame=cv2.resize(frame,(960,max(16,round(frame.shape[0]*960/frame.shape[1]))))
                display=process(frame,time.monotonic())
                latest['frame']=frame;latest['offset']=display.shape[0]-frame.shape[0]
                cv2.imshow(title,display)
                key=cv2.waitKey(1)&255
                if key in (ord('q'),27):break
                if on_key:on_key(key)
                count+=1
                if max_frames and count>=max_frames:break
    finally:cv2.destroyAllWindows()
