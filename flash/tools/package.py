"""Zip the patcher for release: <work>/build/EID_Flash_<version>.zip with eid_flash_patcher.py, the payload and README.

Run build.py first so flash/patcher/eid_flash_payload.json is current.
Usage: python package.py [--work DIR]
"""
import argparse
import json
import os
import zipfile

FLASH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
FILES = ["eid_flash_patcher.py", "eid_flash_payload.json", "README.txt"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("EID_FLASH_WORK", os.path.expanduser("~/flash-isaac-decomp")))
    a = ap.parse_args()
    patcher = os.path.join(FLASH, "patcher")
    version = json.load(open(os.path.join(patcher, "eid_flash_payload.json"), encoding="utf-8"))["version"]
    if version.endswith("-debug"):
        raise SystemExit("payload is a debug build; run build.py without --debug first")
    out = os.path.join(a.work, "build", f"EID_Flash_{version}.zip")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in FILES:
            z.write(os.path.join(patcher, f), os.path.join("EID_Flash", f))
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
