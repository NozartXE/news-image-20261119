#!/usr/bin/env python3
"""Deliver entry.png for news-image-20261119.

The entry point the platform runs. It gates the image (whole PNG,
1024x1024, at most 1 MiB, decodable) and copies it to
$MAKEFUN_OUTPUT_DIR/entry.png, creating the directory if needed.
The image itself is drawn by build_image.py from the edition's
content file (see engine/); this file never draws anything.
"""

import os
import shutil
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"
MAX_BYTES = 1_048_576


def main():
    if not SRC.exists():
        sys.exit("entry.png missing — run build_image.py first")
    if SRC.stat().st_size > MAX_BYTES:
        sys.exit("entry.png exceeds the 1 MiB gate")
    with Image.open(SRC) as im:
        im.load()
        if im.size != (1024, 1024):
            sys.exit(f"entry.png is {im.size}, expected (1024, 1024)")
        if im.format != "PNG":
            sys.exit(f"entry.png is {im.format}, expected PNG")
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / "entry.png"
    shutil.copyfile(SRC, dst)
    print(f"delivered {dst} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
