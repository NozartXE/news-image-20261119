#!/usr/bin/env python3
"""Draw the news-image-20261119 entry image from a content file.

Usage: python3 build_image.py [content.json] [out.png]

The content file is the ONLY thing that changes between editions:
the engine (engine/) validates its accounting (story count, scene
count, additive numbers strip) and renders it deterministically —
same content in, byte-identical PNG out. Default content is
content/content-20261119.json; the 2026-11-18 proof file is passed
explicitly for the pre-open proof render.
"""

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from engine.layout import render  # noqa: E402


def main():
    content_path = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        HERE / "content" / "content-20261119.json"
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "entry.png"
    content = json.loads(content_path.read_text())
    img, stats, warnings = render(content)
    img.save(out_path, format="PNG")
    data = out_path.read_bytes()
    print(f"stories={stats['stories']} illustrated={stats['illustrated']} "
          f"continents={stats['continents']} strip={stats['strip']}")
    print(f"{out_path.name}: {len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()}")
    for w in warnings:
        print(f"WARNING: {w}")
    if len(data) > 1_048_576:
        raise SystemExit("entry.png over the 1 MiB gate")


if __name__ == "__main__":
    main()
