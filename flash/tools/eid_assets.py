"""Build the EID Flash asset atlas and AS2 data tables from this repository.

Inputs (all from this repo):
  resources/font/eid_default.fnt (+ pages)     EID bitmap font (BMFont v3 binary)
  resources/gfx/eid_inline_icons.anm2 (+ png)  inline icons ({{Tears}}, {{ArrowUp}}, ...)
  resources/gfx/eid_transform_icons.anm2       item type icons ("active", "familiar")
  flash/data/eid_markup.lua                    EID.InlineIcons, EID.InlineColors, EID.TextReplacementPairs
  flash/descriptions/en_us.lua, item_data.lua  Flash item descriptions

Outputs (into <out_dir>):
  eid_atlas.png        packed glyphs + icons (embedded into the SWF as a bitmap)
  eid_data.as          AS2 tables: glyphs, icons, colors, descriptions, item data
"""
import os
import re
import struct
import sys
import xml.etree.ElementTree as ET

from PIL import Image

REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
FONT = os.path.join(REPO, "resources", "font", "eid_default.fnt")
GFX = os.path.join(REPO, "resources", "gfx")
EID_DATA = os.path.join(REPO, "flash", "data", "eid_markup.lua")
DESC_DIR = os.path.join(REPO, "flash", "descriptions")

# Flash Isaac predates Repentance, so the AB+ stat icon variants are used (same as EID on AB+).
AB_ALIASES = ["Damage", "Speed", "Tears", "Range", "Shotspeed", "Luck", "AngelChance", "DevilChance", "Tearsize"]
PLACEHOLDER = "¤"  # EID:generatePlaceholderString() uses "¤" * iconWidth
BULLET = "\u0007"


def lua_unescape(s):
    return s.replace('\\"', '"').replace("\\\\", "\\")


def parse_fnt(path):
    d = open(path, "rb").read()
    assert d[:4] == b"BMF\x03", "expected binary BMFont v3"
    p, chars, common, pages = 4, {}, None, []
    while p < len(d):
        t, size = d[p], struct.unpack("<I", d[p + 1:p + 5])[0]
        b = d[p + 5:p + 5 + size]
        p += 5 + size
        if t == 2:
            common = struct.unpack("<HH", b[:4])  # lineHeight, base
        elif t == 3:
            pages = [x.decode() for x in b.split(b"\0") if x]
        elif t == 4:
            for i in range(0, size, 20):
                cid, x, y, w, h, xo, yo, xa, pg, _ = struct.unpack("<IHHHHhhhBB", b[i:i + 20])
                chars[cid] = (x, y, w, h, xo, yo, xa, pg)
    return chars, common, pages


def parse_anm2(path):
    """Return {animation: [frame dict, ...]} for the first layer, frames expanded by Delay."""
    root = ET.parse(path).getroot()
    out = {}
    for anim in root.iter("Animation"):
        layer = anim.find("LayerAnimations/LayerAnimation")
        frames = []
        for f in (layer.findall("Frame") if layer is not None else []):
            fr = {k: float(f.get(k)) for k in ("XPosition", "YPosition", "XPivot", "YPivot", "XCrop", "YCrop", "Width", "Height")}
            frames += [fr] * max(1, int(f.get("Delay", "1")))
        out[anim.get("Name")] = frames
    return out


def parse_inline_icons(src):
    """EID.InlineIcons entries using the default inline sprite: name -> (anim, frame, w, h, left, top)."""
    icons = {}
    for m in re.finditer(r'\["([^"]+)"\]\s*=\s*\{\s*"([^"]+)"\s*,\s*(-?\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(-?\d+))?\s*(?:,\s*(-?\d+))?\s*(,[^}]*)?\}', src):
        name, anim, frame, w, h, left, top, rest = m.groups()
        if rest and rest.strip(", "):
            continue  # uses another sprite object (player icons, controller buttons, ...)
        icons[name] = (anim, int(frame), int(w), int(h), int(left) if left else -1, int(top) if top else 0)
    for n in AB_ALIASES:
        if n + "AB" in icons:
            icons[n] = icons[n + "AB"]
    return icons


def parse_colors(src):
    colors = {}
    for m in re.finditer(r'\["(Color\w+)"\]\s*=\s*KColor\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)', src):
        colors[m.group(1)] = tuple(round(float(v) * 255) for v in m.group(2, 3, 4))
    return colors


def parse_replacements(src):
    block = src[src.index("EID.TextReplacementPairs"):]
    block = block[:block.index("\n}")]
    pairs = []
    for m in re.finditer(r'\{"((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\}', block):
        a, b = lua_unescape(m.group(1)), lua_unescape(m.group(2))
        if a.startswith("\\") or a in ("\r\n", "\n", "\r", "\t"):
            continue
        pairs.append((a, b))
    return pairs


def lua_table(src, name):
    """Body of `<name> = { ... }` (top-level table assignment ending with a line that is just '}')."""
    m = re.search(r"^" + re.escape(name) + r"\s*=\s*\{\s*$(.*?)^\}", src, re.M | re.S)
    if not m:
        sys.exit(f"table {name} not found")
    return m.group(1)


def parse_descriptions():
    """Returns ({table: {id: (name, desc)}}, strings, item_data, card_ids, pill_effects)."""
    src = open(os.path.join(DESC_DIR, "en_us.lua"), encoding="utf-8").read()
    tables = {}
    for t in ("collectibles", "trinkets", "cards", "pills"):
        body = lua_table(src, "EID.descriptions[languageCode]." + t)
        tables[t] = {int(m.group(1)): (lua_unescape(m.group(2)), lua_unescape(m.group(3)))
                     for m in re.finditer(r'\{"(\d+)",\s*"((?:[^"\\]|\\.)*)",\s*"((?:[^"\\]|\\.)*)"\}', body)}
    strings = {m.group(1): lua_unescape(m.group(2))
               for m in re.finditer(r'^EID\.descriptions\[languageCode\]\.(\w+)\s*=\s*"((?:[^"\\]|\\.)*)"', src, re.M)}

    src = open(os.path.join(DESC_DIR, "item_data.lua"), encoding="utf-8").read()
    data = {int(m.group(1)): (m.group(2), int(m.group(3)) if m.group(3) else -1)
            for m in re.finditer(r'\[(\d+)\]\s*=\s*\{"(\w+)"(?:,\s*(\d+))?\}', lua_table(src, "EID.FlashItemData"))}
    cards = {int(a): int(b) for a, b in re.findall(r"\[(\d+)\]\s*=\s*(\d+)", lua_table(src, "EID.FlashCardIDs"))}
    pills = {int(a): (int(b), int(c)) for a, b, c in
             re.findall(r"\[(\d+)\]\s*=\s*\{(\d+),\s*(\d+)\}", lua_table(src, "EID.FlashPillEffects"))}
    return tables, strings, data, cards, pills


class Packer:
    """Simple shelf packer with 1px padding."""

    def __init__(self, width):
        self.w, self.x, self.y, self.row = width, 0, 0, 0
        self.items = []

    def add(self, img):
        if self.x + img.width + 1 > self.w:
            self.x, self.y, self.row = 0, self.y + self.row + 1, 0
        pos = (self.x, self.y)
        self.items.append((img, pos))
        self.x += img.width + 1
        self.row = max(self.row, img.height)
        return pos

    def image(self):
        out = Image.new("RGBA", (self.w, self.y + self.row + 1), (0, 0, 0, 0))
        for img, pos in self.items:
            out.paste(img, pos)
        return out


def as2_str(s):
    out = []
    for ch in s:
        if ch in '"\\':
            out.append("\\" + ch)
        elif ord(ch) < 32 or ord(ch) > 126:
            out.append("\\u%04X" % ord(ch))
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def build(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    eid_src = open(EID_DATA, encoding="utf-8").read()
    chars, (line_height, base), pages = parse_fnt(FONT)
    page_imgs = [Image.open(os.path.join(os.path.dirname(FONT), p)).convert("RGBA") for p in pages]
    icons = parse_inline_icons(eid_src)
    colors = parse_colors(eid_src)
    replacements = parse_replacements(eid_src)
    tables, strings, item_data, card_ids, pill_effects = parse_descriptions()
    inline_anm = parse_anm2(os.path.join(GFX, "eid_inline_icons.anm2"))
    inline_png = Image.open(os.path.join(GFX, "eid_inline_icons.png")).convert("RGBA")
    type_anm = parse_anm2(os.path.join(GFX, "eid_transform_icons.anm2"))
    type_png = Image.open(os.path.join(GFX, "eid_transform_icons.png")).convert("RGBA")

    # apply EID's text replacements (↑ -> {{ArrowUp}}, {{CR}} -> {{ColorReset}}, ...) at build time
    def replace(s):
        for a, b in replacements:
            s = s.replace(a, b)
        return s

    tables = {t: {k: (n, replace(d)) for k, (n, d) in entries.items()} for t, entries in tables.items()}

    used_icons = set(["ArrowUp", "ArrowDown"] + [str(i) for i in range(13)])
    text = "".join(strings.values())
    for entries in tables.values():
        for name, desc in entries.values():
            text += name + desc
            used_icons.update(m for m in re.findall(r"\{\{(.*?)\}\}", desc) if not m.startswith("Color"))
    missing = sorted(i for i in used_icons if i not in icons)
    if missing:
        sys.exit(f"unknown inline icons in descriptions: {missing}")
    used_colors = set(re.findall(r"\{\{(Color\w+)\}\}", text)) | {"ColorEIDText", "ColorEIDObjName"}

    needed = set(chr(c) for c in range(32, 127)) | set(re.sub(r"\{\{.*?\}\}", "", text)) | {BULLET, PLACEHOLDER}
    packer = Packer(512)
    glyph_lines, icon_lines = [], []
    for ch in sorted(needed):
        g = chars.get(ord(ch))
        if g is None:
            print("warning: font has no glyph for", repr(ch))
            continue
        x, y, w, h, xo, yo, xa, pg = g
        if w and h:
            ax, ay = packer.add(page_imgs[pg].crop((x, y, x + w, y + h)))
        else:
            ax = ay = 0
        glyph_lines.append(f"G[{ord(ch)}]=[{ax},{ay},{w},{h},{xo},{yo},{xa}];")

    def add_icon(key, frames, png, frame, eid_w, left, top):
        fr = frames[frame]
        crop = (int(fr["XCrop"]), int(fr["YCrop"]), int(fr["XCrop"] + fr["Width"]), int(fr["YCrop"] + fr["Height"]))
        ax, ay = packer.add(png.crop(crop))
        dx, dy = int(fr["XPosition"] - fr["XPivot"]), int(fr["YPosition"] - fr["YPivot"])
        icon_lines.append(f'I[{as2_str(key)}]=[{ax},{ay},{int(fr["Width"])},{int(fr["Height"])},{dx},{dy},{eid_w},{left},{top}];')

    for name in sorted(used_icons):
        anim, frame, w, h, left, top = icons[name]
        add_icon(name, inline_anm[anim], inline_png, frame, w, left, top)
    for typ in ("active", "familiar"):  # EID.IconSprite item type icons (printDescription header)
        add_icon("type_" + typ, type_anm[typ], type_png, 0, 0, 0, 0)

    atlas = packer.image()
    atlas.save(os.path.join(out_dir, "eid_atlas.png"))

    lines = [
        "// GENERATED by flash/tools/eid_assets.py from the EID repository. Do not edit.",
        f"_root.eidLineHeight = {line_height};",
        f"_root.eidPlaceholder = {ord(PLACEHOLDER)};",
        "var G = _root.eidGlyph = [];",
        *glyph_lines,
        "var I = _root.eidIcon = {};",
        *icon_lines,
        "var C = _root.eidColor = {};",
        *[f"C[{as2_str(c)}]=0x{colors[c][0]:02X}{colors[c][1]:02X}{colors[c][2]:02X};" for c in sorted(used_colors) if c in colors],
        "var D = _root.eidDesc = {};",
    ]
    for t in ("collectibles", "trinkets", "cards", "pills"):
        lines.append(f"D.{t} = [];")
        lines += [f"D.{t}[{k}]=[{as2_str(n)},{as2_str(d)}];" for k, (n, d) in sorted(tables[t].items())]
    lines += [
        f'_root.eidUnidentifiedPill = {as2_str(strings.get("unidentifiedPill", "Unidentified Pill"))};',
        "var T = _root.eidItemData = [];",
        *[f'T[{k}]=["{t}",{c}];' for k, (t, c) in sorted(item_data.items())],
        "var M = _root.eidCardIDs = [];",
        *[f"M[{k}]={v};" for k, v in sorted(card_ids.items())],
        "var P = _root.eidPillEffects = [];",
        *[f"P[{k}]=[{a},{b}];" for k, (a, b) in sorted(pill_effects.items())],
    ]
    open(os.path.join(out_dir, "eid_data.as"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
    print(f"atlas {atlas.size}, {len(glyph_lines)} glyphs, {len(icon_lines)} icons, "
          + ", ".join(f"{len(v)} {k}" for k, v in tables.items()))


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "flash", "build"))
