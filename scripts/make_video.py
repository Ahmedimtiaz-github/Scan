#!/usr/bin/env python3
"""
Standalone video maker from keyframes (cross-dissolve).
Use when OpenCV is available but video_maker/video_adapter are not.
Usage: python scripts/make_video.py <keyframe1.png> <keyframe2.png> ... -o output.mp4
"""

import argparse
import sys

try:
    import cv2
except ImportError:
    print("OpenCV required: pip install opencv-python-headless")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("keyframes", nargs="+", help="Paths to keyframe images")
    parser.add_argument("-o", "--output", default="output.mp4", help="Output video path")
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--crossfade", type=int, default=6)
    parser.add_argument("--hold", type=int, default=12)
    args = parser.parse_args()

    if not args.keyframes:
        print("No keyframes provided")
        sys.exit(1)

    first = cv2.imread(args.keyframes[0])
    if first is None:
        print(f"Cannot read {args.keyframes[0]}")
        sys.exit(1)

    h, w = first.shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(args.output, fourcc, args.fps, (w, h))

    for i, path in enumerate(args.keyframes):
        img = cv2.imread(path)
        if img is None:
            continue
        if img.shape[:2] != (h, w):
            img = cv2.resize(img, (w, h))
        for _ in range(args.hold):
            out.write(img)
        if i < len(args.keyframes) - 1:
            nxt = cv2.imread(args.keyframes[i + 1])
            if nxt is not None:
                if nxt.shape[:2] != (h, w):
                    nxt = cv2.resize(nxt, (w, h))
                for f in range(args.crossfade):
                    alpha = f / args.crossfade
                    blended = cv2.addWeighted(img, 1 - alpha, nxt, alpha, 0)
                    out.write(blended)

    out.release()
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
