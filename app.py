#!/usr/bin/env python3
"""QR Camera Reader: local decoding, no URL opening or code execution."""
import argparse
from pathlib import Path
import sys
import cv2
from camera_utils import camera_loop,header,read_image,export_pair
from core import detect,annotate,escaped,Session


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('camera');a.add_argument('--camera',type=int,default=0);a.add_argument('--max-frames',type=int)
    a=sub.add_parser('demo');a.add_argument('--output')
    a=sub.add_parser('image');a.add_argument('input');a.add_argument('--output')
    args=p.parse_args(argv)
    try:
        if args.command=='camera':
            session=Session()
            def process(frame,t):
                codes=detect(frame);n=session.update(codes)
                lines=[f'QR CAMERA | visible {len(codes)} | unique complete payloads {n}'+(' | CACHE FULL' if session.limit_reached else ''),
                       'Q exit | R reset session | data is displayed only; links are NEVER opened']
                lines += [f'QR {i+1}: '+escaped(c['text'])+(' [TRUNCATED]' if c['truncated'] else '') for i,c in enumerate(codes[:4])]
                return header(annotate(frame,codes),lines)
            camera_loop('QR Camera Reader',process,camera=args.camera,max_frames=args.max_frames,on_key=lambda k:session.reset() if k==ord('r') else None)
        else:
            source=Path(__file__).resolve().parent/'examples/two-codes.png' if args.command=='demo' else Path(args.input)
            image=read_image(source);codes=detect(image)
            output=header(annotate(image,codes),['QR CAMERA READER | explicit local export',f'Decoded {len(codes)} codes; payloads are in JSON. No links opened.'])
            result={'kind':'SYNTHETIC_FIXTURE' if args.command=='demo' else 'LOCAL_IMAGE_RESULT','codes':codes,'note':'No payload executed or opened. No accuracy benchmark.'}
            png,meta=export_pair(output,result,args.output);print(f'Decoded {len(codes)} code(s).\n{png}\n{meta}')
        return 0
    except (ValueError,OSError,RuntimeError,cv2.error) as e:print(f'Error: {e}',file=sys.stderr);return 2
    except KeyboardInterrupt:return 130
if __name__=='__main__':raise SystemExit(main())
