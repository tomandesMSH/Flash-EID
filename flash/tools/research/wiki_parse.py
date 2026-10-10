"""Parse wiki/raw/*.wiki (from wiki_fetch.py) into wiki/items_wiki.json keyed by Flash game item id.

Matches by infobox id when present, else by normalized name against items_flash.json.
"""
import glob
import json
import os
import re

ROOT = os.environ.get("EID_FLASH_WORK", os.path.expanduser("~/flash-isaac-decomp"))
game = {int(k): v for k, v in json.load(open(os.path.join(ROOT, "items_flash.json"))).items()}
ALIASES = {"monstermanuel": "monstermanual", "3": "lessthanthree"}


def norm(s):
    s = re.sub(r"[^a-z0-9]", "", s.lower().replace("'", ""))
    s = re.sub(r"^the", "", s)
    return ALIASES.get(s, s)


by_name = {norm(v["name"]): k for k, v in game.items()}


def section(text, name):
    m = re.search(r"^==\s*(?:" + name + r")\s*==\s*$(.*?)(?=^==[^=]|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def clean(s):
    s = re.sub(r"<ref[^>]*?/>|<ref.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\[\[File:[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    for _ in range(3):
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"[ \t]+", " ", s).strip()


items, unmatched = {}, []
for fn in sorted(glob.glob(os.path.join(ROOT, "wiki", "raw", "*.wiki"))):
    text = open(fn, encoding="utf-8").read()
    title = os.path.basename(fn)[:-5]
    box = re.match(r"\s*\{\{\s*(Infobox item|Item)\b(.*?)\n\}\}|\s*\{\{\s*(Infobox item|Item)\b(.*?)\}\}\s*\n", text, re.S | re.I)
    head = text[:3000]
    typ = re.search(r"\|\s*type\s*=\s*([^\n|]*)", head)
    typ = clean(typ.group(1)) if typ else ""
    if "trinket" in typ.lower():
        continue
    m = re.search(r"\|\s*id\s*=\s*(\d+)", head)
    iid = by_name.get(norm(title)) or (int(m.group(1)) if m else None)
    if iid is None or iid not in game:
        unmatched.append((title, typ))
        continue
    if iid in items and norm(items[iid]["title"]) == norm(game[iid]["name"]):
        continue
    quote = re.search(r"\|\s*quote\s*=\s*([^\n]*)", head)
    items[iid] = {
        "title": title,
        "wiki_id": int(m.group(1)) if m else None,
        "game_name": game[iid]["name"],
        "type": typ,
        "quote": clean(quote.group(1)).strip('"') if quote else "",
        "effects": clean(section(text, "Effects?")),
        "notes": clean(section(text, "Notes")),
        "interactions": clean(section(text, "Interactions|Synergies")),
    }

json.dump(dict(sorted(items.items())), open(os.path.join(ROOT, "wiki", "items_wiki.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print(len(items), "matched;", len(game) - len(items), "game items without page")
print("missing ids:", [k for k in game if k not in items])
print("unmatched pages:", unmatched)
mism = [(k, v["game_name"], v["title"]) for k, v in items.items() if norm(v["game_name"]) != norm(v["title"])]
print("id/name disagreements:", mism)
print("no effects text:", [k for k, v in items.items() if not v["effects"]])
