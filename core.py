"""Local QR decoding. Payloads are data: never opened, executed or sent to a server."""
from __future__ import annotations
import cv2
import numpy as np
from camera_utils import validate_frame,finite


def escaped(text,limit=120):
    # Printable ASCII only. Control characters, newlines and Unicode are escaped.
    return str(text).encode('unicode_escape').decode('ascii')[:limit]


def detect(image):
    validate_frame(image)
    ok,texts,points,_=cv2.QRCodeDetector().detectAndDecodeMulti(image)
    if not ok or points is None:return []
    output=[];h,w=image.shape[:2]
    for text,p in list(zip(texts,points))[:32]:
        if not text:continue
        p=np.asarray(p,dtype=float)
        if p.shape!=(4,2) or not np.isfinite(p).all() or (p[:,0]<0).any() or (p[:,0]>=w).any() or (p[:,1]<0).any() or (p[:,1]>=h).any():continue
        # Decode can succeed with a long payload. Keep memory/exports bounded and disclose truncation.
        output.append({'text':text[:2048],'truncated':len(text)>2048,'corners':p.tolist()})
    return output


class Session:
    def __init__(self):self.seen=set();self.limit_reached=False
    def update(self,codes):
        for c in codes:
            if c['truncated']:continue  # A prefix is not a unique complete QR identity.
            if c['text'] not in self.seen:
                if len(self.seen)>=512:self.limit_reached=True
                else:self.seen.add(c['text'])
        return len(self.seen)
    def reset(self):self.seen.clear();self.limit_reached=False


def annotate(image,codes):
    out=image.copy()
    for i,c in enumerate(codes):
        p=np.round(c['corners']).astype(np.int32)
        cv2.polylines(out,[p],True,(80,210,120),2)
        cv2.putText(out,f'QR {i+1}',tuple(p[0]),cv2.FONT_HERSHEY_SIMPLEX,.6,(80,210,120),2)
    return out
