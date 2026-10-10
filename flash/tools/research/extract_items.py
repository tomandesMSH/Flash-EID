"""Extract Flash Isaac item names (st1) and pickup captions (st2x) from the decompiled root script."""
import json
import os
import re

ROOT = os.environ.get("EID_FLASH_WORK", os.path.expanduser("~/flash-isaac-decomp"))
src = open(os.path.join(ROOT, "decomp/scripts/frame_1/DoAction.as"), encoding="utf-8").read()
TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|(-?\d+)')


def arr(name):
    line = next(l for l in src.splitlines() if l.startswith(name + " = ["))
    body = line[len(name) + 4:-2]
    return [m.group(1).replace("\\'", "'") if m.group(1) is not None else int(m.group(2))
            for m in TOKEN.finditer(body)]


st1, st2 = arr("st1"), arr("st2x")
items = {i: {"name": st1[i], "caption": st2[i] if i < len(st2) else None} for i in range(1, len(st1))}
json.dump(items, open(os.path.join(ROOT, "items_flash.json"), "w"), indent=1)
print(len(items), "items")
for i in list(items)[:5] + list(items)[-5:]:
    print(i, items[i])
