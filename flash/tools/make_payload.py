"""Build the patcher payload (flash/patcher/eid_flash_payload.json) from this repository.

The payload holds only EID's own content, never game code:
  - doaction: a complete DoAction tag with the compiled EID code (generated eid_data.as + as2/eid_flash.as)
  - bitmaps:  the EID font/icon atlas as a DefineBitsLossless2 body without its character id
The patcher inserts both into frame 1 of the user's own game SWF (see patcher/eid_flash_patcher.py).

Our AS2 is compiled on its own: a minimal one-frame SWF with an empty DoAction is generated, FFDec replaces that
script with ours, and the resulting DoAction tag is taken out again. Needs Pillow and FFDec (see build.py).

Usage: python make_payload.py [--debug] [--work DIR] [--out FILE]
"""
import argparse
import base64
import json
import os
import re
import struct
import subprocess
import sys
import zlib

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FLASH = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(FLASH, ".."))
sys.dont_write_bytecode = True  # keep __pycache__ out of flash/patcher (it is distributed as-is)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(FLASH, "patcher"))
import eid_assets  # noqa: E402
import eid_flash_patcher as patcher  # noqa: E402

# SHA-256 of the decrypted game SWF this release was tested with (Steam, Wrath of the Lamb / Eternal Edition v1.666)
TESTED_GAME_SHA256 = ["ef03b6ce5ae72a8b8ed3859f29ce4efa24e3abf21357ad658b7de3a66b6dc725"]


def ffdec_cmd(work):
    import build
    return build.find_tools(work)


def minimal_swf():
    """SWF 8, 800x600, one frame: FileAttributes, SetBackgroundColor, empty DoAction, ShowFrame, End."""
    nbits = 15
    bits = f"{nbits:05b}" + "".join(f"{v:0{nbits}b}" for v in (0, 16000, 0, 12000))
    bits += "0" * (-len(bits) % 8)
    rect = int(bits, 2).to_bytes(len(bits) // 8, "big")
    tags = (patcher.tag_header(69, 4) + struct.pack("<I", 0)
            + patcher.tag_header(9, 3) + b"\0\0\0"
            + patcher.tag_header(12, 1) + b"\0"
            + patcher.tag_header(1, 0)
            + patcher.tag_header(0, 0))
    body = rect + struct.pack("<HH", 30 << 8, 1) + tags
    return b"FWS" + bytes([8]) + struct.pack("<I", 8 + len(body)) + body


def compile_as2(script_path, work, tmp_dir):
    src, out = os.path.join(tmp_dir, "empty.swf"), os.path.join(tmp_dir, "compiled.swf")
    open(src, "wb").write(minimal_swf())
    if os.path.exists(out):
        os.remove(out)
    r = subprocess.run(ffdec_cmd(work) + ["-replace", src, out, "\\frame_1\\DoAction", script_path],
                       capture_output=True, text=True)
    log = r.stdout + r.stderr
    if r.returncode != 0 or not os.path.exists(out) or re.search(r"\berror\b", log, re.I):
        sys.exit("AS2 compile failed:\n" + log[-3000:])
    d = patcher.decompress(open(out, "rb").read())
    for code, start, body, length in patcher.walk_tags(d, patcher.first_tag_offset(d), len(d)):
        if code == 12:
            return d[start:body + length]
    sys.exit("compiled SWF has no DoAction")


def lossless2_body(png):
    """DefineBitsLossless2 body without the leading character id: format 5 (32-bit), premultiplied ARGB."""
    img = Image.open(png).convert("RGBA")
    raw = bytearray()
    for r, g, b, a in img.getdata():
        raw += bytes((a, r * a // 255, g * a // 255, b * a // 255))
    return struct.pack("<BHH", 5, img.width, img.height) + zlib.compress(bytes(raw), 9)


def eid_version():
    return open(os.path.join(FLASH, "VERSION"), encoding="utf-8").read().strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--debug", action="store_true", help="include the test hooks (as2/eid_debug.as)")
    ap.add_argument("--work", default=os.environ.get("EID_FLASH_WORK", os.path.expanduser("~/flash-isaac-decomp")))
    ap.add_argument("--out", default=os.path.join(FLASH, "patcher", "eid_flash_payload.json"))
    a = ap.parse_args()
    make(a.work, a.out, a.debug)


def make(work, out, debug=False):
    tmp = os.path.join(work, "build", "payload")
    os.makedirs(tmp, exist_ok=True)
    eid_assets.build(tmp)
    parts = [open(os.path.join(FLASH, "as2", "eid_host.as"), encoding="utf-8").read(),
             open(os.path.join(tmp, "eid_data.as"), encoding="utf-8").read(),
             open(os.path.join(FLASH, "as2", "eid_flash.as"), encoding="utf-8").read()]
    if debug:
        parts.append(open(os.path.join(FLASH, "as2", "eid_debug.as"), encoding="utf-8").read())
    script = os.path.join(tmp, "eid_script.as")
    with open(script, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    payload = {
        "version": eid_version() + ("-debug" if debug else ""),
        "game_sha256": TESTED_GAME_SHA256,
        "doaction": base64.b64encode(compile_as2(script, work, tmp)).decode(),
        "bitmaps": [{"name": "eid_atlas", "lossless2": base64.b64encode(lossless2_body(os.path.join(tmp, "eid_atlas.png"))).decode()}],
    }
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=1)
        f.write("\n")
    print(f"payload {out}: {os.path.getsize(out)} bytes")
    return out


if __name__ == "__main__":
    main()
