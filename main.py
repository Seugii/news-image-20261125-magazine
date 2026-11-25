#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261125 (magazine, THE BURNING SEA).

Copies the pre-rendered entry.png (in this repository) to the output
directory the grader provides. Standard library only.
"""
import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND_TRAILER = b"IEND\xaeB`\x82"
MAX_BYTES = 1048576  # 1 MiB gate limit


def check_png(path):
    """Return (ok, reason). Validates magic, IEND trailer and size."""
    size = os.path.getsize(path)
    if size > MAX_BYTES:
        return False, "entry.png is %d bytes, over the 1 MiB limit" % size
    with open(path, "rb") as f:
        head = f.read(8)
        if head != PNG_MAGIC:
            return False, "entry.png is not a PNG file"
        f.seek(-12, os.SEEK_END)
        tail = f.read(12)
    if not tail.endswith(IEND_TRAILER):
        return False, "entry.png has no IEND trailer (truncated PNG)"
    return True, "ok (%d bytes)" % size


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
    print("wrote", dst, info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
