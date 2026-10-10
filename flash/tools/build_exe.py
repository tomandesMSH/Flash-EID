"""Build EID_Flash_Patcher.exe (single file, payload bundled) with PyInstaller.

Run build.py first so flash/patcher/eid_flash_payload.json is current.
Usage: python build_exe.py [--work DIR]      (needs: pip install pyinstaller)
Output: <work>/build/exe/EID_Flash_Patcher.exe
"""
import argparse
import json
import os
import subprocess
import sys

FLASH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PATCHER = os.path.join(FLASH, "patcher")

VERSION_INFO = """VSVersionInfo(
  ffi=FixedFileInfo(filevers=({v}, 0), prodvers=({v}, 0), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1,
                    subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('FileDescription', 'EID Flash patcher: builds External Item Descriptions for The Binding of Isaac (Flash) from your own copy'),
      StringStruct('FileVersion', '{s}'),
      StringStruct('InternalName', 'EID_Flash_Patcher'),
      StringStruct('OriginalFilename', 'EID_Flash_Patcher.exe'),
      StringStruct('ProductName', 'EID Flash (unofficial port of External Item Descriptions)'),
      StringStruct('ProductVersion', '{s}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("EID_FLASH_WORK", os.path.expanduser("~/flash-isaac-decomp")))
    a = ap.parse_args()
    payload = os.path.join(PATCHER, "eid_flash_payload.json")
    version = json.load(open(payload, encoding="utf-8"))["version"]
    if version.endswith("-debug"):
        sys.exit("payload is a debug build; run build.py without --debug first")
    parts = [int(x) for x in version.split(".")] + [0, 0, 0]
    build = os.path.join(a.work, "build", "pyinstaller")
    os.makedirs(build, exist_ok=True)
    vfile = os.path.join(build, "version_info.txt")
    open(vfile, "w", encoding="utf-8").write(VERSION_INFO.format(v=", ".join(map(str, parts[:3])), s=version))
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--console",
           "--name", "EID_Flash_Patcher", "--version-file", vfile,
           "--add-data", payload + os.pathsep + ".",
           "--distpath", os.path.join(a.work, "build", "exe"), "--workpath", build, "--specpath", build,
           os.path.join(PATCHER, "eid_flash_patcher.py")]
    r = subprocess.run(cmd)
    if r.returncode != 0:
        sys.exit("PyInstaller failed")
    exe = os.path.join(a.work, "build", "exe", "EID_Flash_Patcher.exe")
    print("built", exe, os.path.getsize(exe), "bytes")


if __name__ == "__main__":
    main()
