"""Fetch the Flash-era wiki pages for trinkets, tarot cards and pills (raw wikitext) into <work>/wiki/raw_pickups.

Usage: python wiki_fetch_pickups.py
Wiki text is CC BY-SA 3.0 (bindingofisaac.fandom.com); only used as reference for paraphrased descriptions.
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
OUT = os.path.join(ROOT, "wiki", "raw_pickups")
os.makedirs(OUT, exist_ok=True)


def api(**params):
    params["format"] = "json"
    req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


titles = [m["title"] for m in api(action="query", list="categorymembers", cmtitle="Category:Trinkets",
                                  cmlimit=500, cmnamespace=0)["query"]["categorymembers"]]
titles += ["Tarot Cards", "Pills", "Trinkets", "Playing Cards", "Joker"]
for i in range(0, len(titles), 40):
    r = api(action="query", prop="revisions", rvprop="content", rvslots="main", redirects=1,
            titles="|".join(titles[i:i + 40]))
    for page in r["query"]["pages"].values():
        if "revisions" in page:
            name = re.sub(r'[\\/:*?"<>|]', "_", page["title"])
            open(os.path.join(OUT, name + ".wiki"), "w", encoding="utf-8").write(page["revisions"][0]["slots"]["main"]["*"])
    time.sleep(1)
print(len(os.listdir(OUT)), "pages saved to", OUT)
