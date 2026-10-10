"""Developer helper: dump the decrypted game SWF to <work>/isaac.swf (uses the patcher's dump code).

Usage: python swfdump.py [--game DIR] [--work DIR] [--wait SECONDS]
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "patcher"))
import eid_flash_patcher as patcher  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default=None, help="game folder containing Isaac.exe (default: Steam install)")
    ap.add_argument("--work", default=os.environ.get("EID_FLASH_WORK", os.path.expanduser("~/flash-isaac-decomp")))
    ap.add_argument("--wait", type=int, default=30)
    a = ap.parse_args()
    game = a.game or patcher.find_game()
    if not game:
        sys.exit("game not found; use --game")
    swf = patcher.dump_swf(game, a.wait)
    os.makedirs(a.work, exist_ok=True)
    out = os.path.join(a.work, "isaac.swf")
    open(out, "wb").write(swf)
    print("wrote", out, len(swf), "bytes")


if __name__ == "__main__":
    main()
