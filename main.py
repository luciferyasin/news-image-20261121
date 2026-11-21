#!/usr/bin/env python3
"""Entry point: copy the built entry image to the make.fun output dir.

The organiser reads exactly one image from $MAKEFUN_OUTPUT_DIR; the
copy is byte-identical to the entry.png produced by build_image.py.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(HERE, "output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SRC, dst)
    same = open(SRC, "rb").read() == open(dst, "rb").read()
    print(f"copied {SRC} -> {dst} ({os.path.getsize(dst)} bytes, identical={same})")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
