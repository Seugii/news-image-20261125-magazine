#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261125 (magazine, THE BURNING SEA).

Copies the pre-rendered entry.png (in this repository) to the output
directory the grader provides. Standard library only.

Revision (user direction): the masthead is now the date itself in a
Vogue-style Didone serif (Playfair Display), with the cover title
below it on the cream page background — no red masthead band, no
dateline strip, no headline overlaid on the cover photo. Validation
extended in this revision: PNG dimensions must be exactly 1024x1024
(parsed from the IHDR chunk) and the SHA-256 digest is printed.
"""
import hashlib
import os
import shutil
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND_TRAILER = b"IEND\xaeB`\x82"
MAX_BYTES = 1048576  # 1 MiB gate limit
EXPECT_W, EXPECT_H = 1024, 1024


def check_png(path):
    """Return (ok, reason). Validates magic, IHDR size, IEND trailer, size."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        return False, "entry.png is %d bytes, over the 1 MiB limit" % size
    with open(path, "rb") as f:
        head = f.read(8)
        if head != PNG_MAGIC:
            return False, "entry.png is not a PNG file"
        ihdr = f.read(25)
        if len(ihdr) < 25 or ihdr[4:8] != b"IHDR":
            return False, "entry.png has no IHDR chunk"
        w, h = struct.unpack(">II", ihdr[8:16])
        if (w, h) != (EXPECT_W, EXPECT_H):
            return False, "entry.png is %dx%d, expected %dx%d" % (
                w, h, EXPECT_W, EXPECT_H)
        f.seek(-12, os.SEEK_END)
        tail = f.read(12)
    if not tail.endswith(IEND_TRAILER):
        return False, "entry.png has no IEND trailer (truncated PNG)"
    return True, "ok (%d bytes, %dx%d)" % (size, w, h)


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    ok, info = check_png(src)
    if not ok:
        print(info, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote", dst, info, "sha256", sha256_file(dst))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
