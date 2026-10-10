"""External Item Descriptions for The Binding of Isaac (Flash): patcher.

Builds a modded copy of the game from YOUR OWN installation. No game files are distributed: this script
reads the game from your PC and adds EID's code and graphics (eid_flash_payload.json, next to this script).

Usage: double-click EID_Flash_Patcher.exe (it downloads the projector too), or with Python 3.8+ (no extra packages):
    python eid_flash_patcher.py                    # find the Steam install, build "EID Flash/isaac_eid.swf"
    python eid_flash_patcher.py --game "D:/Games/The Binding Of Isaac"
    python eid_flash_patcher.py --swf isaac.swf    # patch an already extracted SWF instead
    python eid_flash_patcher.py --get-projector    # also download Adobe's Flash Player 32 projector

How it works: the Steam game (Isaac.exe) is an MDM Zinc projector that keeps the game SWF encrypted. The patcher
copies the game folder to a temporary folder, starts that copy for a few seconds, reads the decrypted SWF from its
memory, closes it, and inserts the EID payload into the SWF's first frame. Your installation is never modified.
Play the result with Adobe's standalone Flash Player 32 projector ("Play EID Flash.bat" is created for you).
"""
import argparse
import base64
import ctypes
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.request
import zlib

FROZEN = getattr(sys, "frozen", False)  # running as the PyInstaller exe (EID_Flash_Patcher.exe)
HERE = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))  # the exe bundles the payload
PAYLOAD = os.path.join(HERE, "eid_flash_payload.json")
STEAM_DIRS = [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"]
GAME_SUBDIR = os.path.join("steamapps", "common", "The Binding Of Isaac")
PROJECTOR_URL = "https://fpdownload.macromedia.com/pub/flashplayer/updaters/32/flashplayer_32_sa.exe"
PROJECTOR_SHA256 = "a4b333ac1da12026989549015303d82231982838bccfb544ba5fd188746066f0"

# tags whose body starts with a u16 character id
DEFINE_TAGS = {2, 6, 7, 10, 11, 13, 14, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 46, 48, 60, 62, 75, 83, 84, 87, 90, 91}
TAG_SHOWFRAME, TAG_END, TAG_LOSSLESS2, TAG_EXPORT = 1, 0, 36, 56


# ---------------------------------------------------------------- SWF helpers

def tag_header(code, length):
    if length < 0x3F:
        return struct.pack("<H", (code << 6) | length)
    return struct.pack("<HI", (code << 6) | 0x3F, length)


def first_tag_offset(d):
    nb = d[8] >> 3
    return 8 + (5 + 4 * nb + 7) // 8 + 4


def walk_tags(d, p, end):
    """Yields (code, tag_start, body_start, body_length) up to and including the End tag."""
    while p + 2 <= end:
        h = struct.unpack("<H", d[p:p + 2])[0]
        code, length, start = h >> 6, h & 0x3F, p
        p += 2
        if length == 0x3F:
            length = struct.unpack("<I", d[p:p + 4])[0]
            p += 4
        yield code, start, p, length
        p += length
        if code == TAG_END:
            return


def decompress(d):
    if d[:3] == b"CWS":
        return b"FWS" + d[3:8] + zlib.decompress(d[8:])
    if d[:3] != b"FWS":
        raise ValueError("not an SWF file")
    return d


def tags_ok(d):
    """True if d is an uncompressed SWF whose tag list walks exactly to its End tag."""
    if len(d) < 30 or d[:3] != b"FWS":
        return False
    end = None
    for code, start, body, length in walk_tags(d, first_tag_offset(d), len(d)):
        if code == TAG_END:
            end = body + length
    return end == len(d)


def apply_payload(swf, payload):
    """Insert the payload tags into frame 1 of the root timeline, right before its ShowFrame."""
    d = decompress(swf)
    max_id, show_frame = 0, None
    for code, start, body, length in walk_tags(d, first_tag_offset(d), len(d)):
        if code in DEFINE_TAGS:
            max_id = max(max_id, struct.unpack("<H", d[body:body + 2])[0])
        if show_frame is None and code == TAG_SHOWFRAME:
            show_frame = start
    if show_frame is None:
        raise ValueError("SWF has no frames")
    new = b""
    for i, bitmap in enumerate(payload["bitmaps"]):
        cid = max_id + 1 + i
        body = struct.pack("<H", cid) + base64.b64decode(bitmap["lossless2"])
        new += tag_header(TAG_LOSSLESS2, len(body)) + body
        export = struct.pack("<HH", 1, cid) + bitmap["name"].encode("utf-8") + b"\0"
        new += tag_header(TAG_EXPORT, len(export)) + export
    new += base64.b64decode(payload["doaction"])  # complete DoAction tag (header + actions) with EID's code
    out = d[:show_frame] + new + d[show_frame:]
    return out[:4] + struct.pack("<I", len(out)) + out[8:]


# ---------------------------------------------------------------- dump the SWF from the running game

class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p), ("AllocationProtect", ctypes.c_uint32),
                ("PartitionId", ctypes.c_uint16), ("RegionSize", ctypes.c_size_t), ("State", ctypes.c_uint32),
                ("Protect", ctypes.c_uint32), ("Type", ctypes.c_uint32)]


def scan_process(handle):
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.VirtualQueryEx.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(MBI), ctypes.c_size_t]
    k32.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t,
                                      ctypes.POINTER(ctypes.c_size_t)]
    best, addr, mbi = None, 0, MBI()
    while addr < 0xFFFF0000 and k32.VirtualQueryEx(handle, addr, ctypes.byref(mbi), ctypes.sizeof(mbi)):
        base, size = mbi.BaseAddress or 0, mbi.RegionSize
        if mbi.State == 0x1000 and not (mbi.Protect & 0x101):  # committed, not guard/no-access
            buf, n = ctypes.create_string_buffer(size), ctypes.c_size_t()
            if k32.ReadProcessMemory(handle, base, buf, size, ctypes.byref(n)):
                d = buf.raw[:n.value]
                i = d.find(b"FWS")
                while i != -1:
                    if i + 8 <= len(d):
                        length = struct.unpack("<I", d[i + 4:i + 8])[0]
                        if 1_000_000 < length <= len(d) - i and (best is None or length > len(best)) \
                                and tags_ok(d[i:i + length]):
                            best = d[i:i + length]
                    i = d.find(b"FWS", i + 1)
        addr = base + size
    return best


def dump_swf(game_dir, wait):
    """Copy the game folder to a temp folder, run the copy, read the decrypted SWF from its memory."""
    if not os.path.exists(os.path.join(game_dir, "Isaac.exe")):
        sys.exit(f"Isaac.exe not found in {game_dir} (use --game)")
    tmp = tempfile.mkdtemp(prefix="eid_flash_")
    try:
        for f in os.listdir(game_dir):
            if os.path.isfile(os.path.join(game_dir, f)):
                shutil.copy2(os.path.join(game_dir, f), tmp)
        print("Starting a temporary copy of the game for a few seconds (a game window will appear)...")
        # The copy is not affected by a "Run as administrator" compatibility flag on the original path, and the
        # handle returned to us as the creator keeps full access to read its memory.
        proc = subprocess.Popen([os.path.join(tmp, "Isaac.exe")], cwd=tmp)
        try:
            swf = None
            for _ in range(max(1, wait // 5)):
                time.sleep(5)
                if proc.poll() is not None:
                    sys.exit("The game closed before the SWF could be read.")
                swf = scan_process(int(proc._handle))
                if swf:
                    break
        finally:
            proc.kill()
            proc.wait()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not swf:
        sys.exit("Could not find the game SWF in memory; try again with a longer --wait.")
    return swf


# ---------------------------------------------------------------- main

def find_game():
    for steam in STEAM_DIRS:
        lib_file = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        libs = [steam]
        if os.path.exists(lib_file):
            for line in open(lib_file, encoding="utf-8", errors="ignore"):
                if '"path"' in line:
                    libs.append(line.split('"')[3].replace("\\\\", "\\"))
        for lib in libs:
            if os.path.exists(os.path.join(lib, GAME_SUBDIR, "Isaac.exe")):
                return os.path.join(lib, GAME_SUBDIR)
    return None


def get_projector(out_dir):
    path = os.path.join(out_dir, "flashplayer_32_sa.exe")
    if not os.path.exists(path):
        print("Downloading Adobe Flash Player 32 projector from", PROJECTOR_URL)
        data = urllib.request.urlopen(PROJECTOR_URL, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != PROJECTOR_SHA256:
            sys.exit("Downloaded projector has an unexpected checksum; not saved.")
        open(path, "wb").write(data)
    return path


def main():
    # the exe writes next to itself (double-click), the script into the current folder
    base = os.path.dirname(sys.executable) if FROZEN else os.getcwd()
    ap = argparse.ArgumentParser(description="Build EID for The Binding of Isaac (Flash) from your own copy of the game.")
    ap.add_argument("--game", help="game folder containing Isaac.exe (default: Steam install)")
    ap.add_argument("--swf", help="patch this already extracted game SWF instead of reading it from the game")
    ap.add_argument("--out", default=os.path.join(base, "EID Flash"), help="output folder")
    ap.add_argument("--payload", default=PAYLOAD, help=argparse.SUPPRESS)
    ap.add_argument("--name", default="isaac_eid.swf", help=argparse.SUPPRESS)
    ap.add_argument("--get-projector", action="store_true", default=FROZEN,
                    help="download Adobe's Flash Player 32 projector (default for the exe)")
    ap.add_argument("--no-projector", dest="get_projector", action="store_false", help="don't download the projector")
    ap.add_argument("--wait", type=int, default=30, help="seconds to wait for the game to load (default 30)")
    a = ap.parse_args()

    payload = json.load(open(a.payload, encoding="utf-8"))
    print(f"EID Flash {payload['version']}")
    if a.swf:
        swf = decompress(open(a.swf, "rb").read())
    else:
        if os.name != "nt":
            sys.exit("Reading the game requires Windows; use --swf with an extracted SWF instead.")
        game = a.game or find_game()
        if not game:
            sys.exit("Could not find The Binding of Isaac (Flash) in Steam; use --game \"<folder with Isaac.exe>\".")
        swf = dump_swf(game, a.wait)
    digest = hashlib.sha256(swf).hexdigest()
    if digest not in payload["game_sha256"]:
        print("Warning: this game version differs from the tested one (" + digest[:12] + "); EID may not work.")

    os.makedirs(a.out, exist_ok=True)
    out = os.path.join(a.out, a.name)
    open(out, "wb").write(apply_payload(swf, payload))
    print("Wrote", out)

    projector = get_projector(a.out) if a.get_projector else os.path.join(a.out, "flashplayer_32_sa.exe")
    bat = os.path.join(a.out, "Play EID Flash.bat")
    with open(bat, "w", newline="") as f:
        f.write('@echo off\r\ncd /d "%~dp0"\r\nif not exist flashplayer_32_sa.exe (\r\n'
                '  echo Put flashplayer_32_sa.exe in this folder, or run the patcher with --get-projector.\r\n'
                '  pause\r\n  exit /b 1\r\n)\r\n'
                f'start "" flashplayer_32_sa.exe "{a.name}"\r\n')
    print("Start the game with", bat if os.path.exists(projector) else bat + " (after adding flashplayer_32_sa.exe)")
    print("Note: the modded game keeps its own save data and does not unlock Steam achievements.")


def run():
    """Entry point; when started by double-click (exe), keep the console window open to show the result."""
    code = 0
    try:
        main()
    except SystemExit as e:
        if e.code not in (None, 0):
            print(e.code if isinstance(e.code, str) else f"Exited with code {e.code}")
            code = 1
    except Exception as e:  # show unexpected errors instead of a vanishing window
        print("Error:", e)
        code = 1
    if FROZEN:
        try:
            input("\nPress Enter to close this window...")
        except EOFError:
            pass
    sys.exit(code)


if __name__ == "__main__":
    run()
