"""Fetch Flash-era item pages from bindingofisaac.fandom.com (MediaWiki API) and extract id/quote/effects.

Writes wiki/raw/<title>.wiki and wiki/items_wiki.json ({id: {title, quote, type, effects, notes}}).
Wiki text is CC BY-SA 3.0 (Fandom); only used as reference for paraphrased descriptions.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.environ.get("EID_FLASH_WORK", os.path.expanduser("~/flash-isaac-decomp"))
API = "https://bindingofisaac.fandom.com/api.php"
UA = {"User-Agent": "EID-Flash-research/0.1 (personal mod, low volume)"}
RAW = os.path.join(ROOT, "wiki", "raw")
os.makedirs(RAW, exist_ok=True)


def api(**params):
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def category_members(cat):
    out, cont = [], {}
    while True:
        r = api(action="query", list="categorymembers", cmtitle=cat, cmlimit=500, cmnamespace=0, **cont)
        out += [m["title"] for m in r["query"]["categorymembers"]]
        if "continue" not in r:
            return out
        cont = {"cmcontinue": r["continue"]["cmcontinue"]}


def section(text, name):
    m = re.search(r"^==\s*" + name + r"\s*==\s*$(.*?)(?=^==[^=]|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def clean(s):
    s = re.sub(r"<ref[^>]*?/>|<ref.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"\[\[File:[^\]]*\]\]", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"'''?", "", s)
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"[ \t]+", " ", s).strip()


titles = category_members("Category:Items")
print(len(titles), "pages in Category:Items")
items = {}
for i in range(0, len(titles), 40):
    batch = titles[i:i + 40]
    r = api(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(batch))
    for page in r["query"]["pages"].values():
        if "revisions" not in page:
            continue
        text = page["revisions"][0]["slots"]["main"]["*"]
        title = page["title"]
        open(os.path.join(RAW, re.sub(r'[\\/:*?"<>|]', "_", title) + ".wiki"), "w", encoding="utf-8").write(text)
        m = re.search(r"\|\s*id\s*=\s*(\d+)", text)
        if not m or "{{Infobox item" not in text:
            continue
        typ = re.search(r"\|\s*type\s*=\s*([^\n|]*)", text)
        quote = re.search(r"\|\s*quote\s*=\s*([^\n]*)", text)
        items[int(m.group(1))] = {
            "title": title,
            "type": clean(typ.group(1)) if typ else "",
            "quote": clean(quote.group(1)).strip('"') if quote else "",
            "effects": clean(section(text, "Effects?")),
            "notes": clean(section(text, "Notes")),
            "synergies": clean(section(text, "Synergies")),
        }
    time.sleep(1)
json.dump(dict(sorted(items.items())), open(os.path.join(ROOT, "wiki", "items_wiki.json"), "w", encoding="utf-8"),
          indent=1, ensure_ascii=False)
print(len(items), "item pages with ids")
