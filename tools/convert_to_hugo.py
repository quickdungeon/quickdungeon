#!/usr/bin/env python3
"""Convert the recovered Quick Dungeon archive into Hugo page bundles.

Usage: convert_to_hugo.py ARCHIVE_EXPANSION_DIR SITE_DIR EXPANSION_ID "Expansion Name"
  e.g. convert_to_hugo.py classic site classic Classic

Reads ARCHIVE_EXPANSION_DIR/<slug>/index.html (the cleaned archive pages, with local image
paths) plus manifest.json, and writes:
  SITE_DIR/content/dungeons/<slug>/index.md   structured YAML front matter
  SITE_DIR/content/dungeons/<slug>/images/    only the images the guide uses
  SITE_DIR/data/expansions/<id>.yaml          guide order, taken from the archive index page

Parsing uses BeautifulSoup + lxml, which nests the WordPress markup the same way a browser
does (checked against Chrome's DOM for all 26 Classic guides).
"""
import json, os, re, shutil, sys
from bs4 import BeautifulSoup, NavigableString, Tag

BLOCK_TAGS = {"p", "div", "li", "h3", "h4", "ul", "ol"}


def norm(text):
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def blocks_of(node):
    """Flatten mixed WordPress content into an ordered list of {text} / {image} blocks."""
    out, buf = [], []

    def flush():
        t = norm("".join(buf))
        buf.clear()
        if t.startswith("Archive note:"):  # added during recovery, not the author's text
            out.append({"note": t.split(":", 1)[1].strip()})
        elif t:
            out.append({"text": t})

    def walk(n):
        for c in n.children:
            if isinstance(c, NavigableString):
                buf.append(str(c))
            elif isinstance(c, Tag):
                if c.name == "img":
                    flush()
                    out.append({"image": c["src"]})
                elif c.name == "br":
                    flush()
                elif c.name in BLOCK_TAGS:
                    flush(); walk(c); flush()
                else:
                    walk(c)

    walk(node)
    flush()
    return out


def tabs_after(article, heading):
    h = next((h for h in article.find_all("h2") if norm(h.get_text()).rstrip(":").lower() == heading), None)
    if h is None:
        raise ValueError(f"no '{heading}' heading")
    tabs = h.find_next(class_="su-tabs")
    navs = tabs.select(":scope > .su-tabs-nav > span")
    panes = tabs.select(":scope > .su-tabs-panes > .su-tabs-pane")
    assert len(navs) == len(panes), (heading, len(navs), len(panes))
    return list(zip([norm(n.get_text()) for n in navs], panes))


LABEL_RE = re.compile(r"^(\d+)\.\s*(.+?)(?:\s*\((optional boss|heroic boss)\))?$", re.I)


def parse_boss(label, pane):
    m = LABEL_RE.match(label)
    n, name, tag = (int(m.group(1)), m.group(2), (m.group(3) or "").lower()) if m else (None, label, "")
    img = pane.find("img")
    lines = [norm(l) for l in pane.get_text("\n").split("\n")]
    tactics, heroic = [], []
    for line in filter(None, lines):
        if line.rstrip(":").lower() == "quick boss tactics":
            continue
        if line.lower().startswith("heroic differences:"):
            heroic.append(line.split(":", 1)[1].strip())
        else:  # "/i ..." lines; one boss (Roogug) is missing the /i prefix
            tactics.append(re.sub(r"^/i\s*", "", line))
    boss = {"number": n, "name": name}
    if tag:
        boss["tag"] = {"optional boss": "optional", "heroic boss": "heroic"}[tag]
    if img is not None:
        boss["image"] = img["src"]
    boss["tactics"] = tactics
    if heroic:
        boss["heroic"] = " ".join(heroic)
    return boss


def parse_guide(path):
    soup = BeautifulSoup(open(path, encoding="utf-8").read(), "lxml")
    art = soup.find("article")
    title = norm(soup.find("h1").get_text())
    intro = art.find("p")
    lines = [norm(l) for l in intro.get_text("\n").split("\n") if norm(l)]
    where = next(l for l in lines if l.startswith("You can find"))
    zm = re.search(r"\bwithin\s+(.+?),\s*([^,]+?)\.?$", where)
    cm = re.search(r"The coordinates(?: of (.+?))? (?:are|is) \(\s*([\d.]+)\s*,\s*([\d.]+)\s*\)", " ".join(lines))
    spoiler = art.find(class_="su-spoiler")
    guide = {
        "title": title,
        "zone": zm.group(1),
        "continent": zm.group(2),
        "coords": {"x": float(cm.group(2)), "y": float(cm.group(3))},
        "entrance": blocks_of(spoiler.find(class_="su-spoiler-content")) if spoiler else [],
        "route": [{"label": label, "blocks": blocks_of(pane)} for label, pane in tabs_after(art, "route")],
        "bosses": [parse_boss(label, pane) for label, pane in tabs_after(art, "bosses")],
    }
    if cm.group(1):
        guide["coords"]["label"] = cm.group(1)
    return guide


# --- tiny YAML emitter: JSON-quoted strings are valid YAML double-quoted scalars ---------
# Keys that YAML 1.1 parsers (including Hugo's) read as booleans must be quoted.
AMBIGUOUS_KEYS = {"y", "n", "yes", "no", "on", "off", "true", "false"}


def y_key(k):
    return json.dumps(k) if k.lower() in AMBIGUOUS_KEYS else k

def y_scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    return json.dumps(v, ensure_ascii=False)


def y_dump(v, indent=0):
    pad = "  " * indent
    out = []
    if isinstance(v, dict):
        for k, val in v.items():
            if isinstance(val, (dict, list)) and val:
                out.append(f"{pad}{y_key(k)}:")
                out.append(y_dump(val, indent + 1))
            elif isinstance(val, (dict, list)):
                out.append(f"{pad}{y_key(k)}: {'{}' if isinstance(val, dict) else '[]'}")
            else:
                out.append(f"{pad}{y_key(k)}: {y_scalar(val)}")
    else:
        for item in v:
            if isinstance(item, dict):
                body = y_dump(item, indent + 1).split("\n")
                out.append(f"{pad}- {body[0].lstrip()}")
                out.extend(body[1:])
            else:
                out.append(f"{pad}- {y_scalar(item)}")
    return "\n".join(out)


def main():
    archive, site, exp_id, exp_name = sys.argv[1:5]
    manifest = json.load(open(os.path.join(archive, "manifest.json")))
    index = BeautifulSoup(open(os.path.join(archive, "index.html"), encoding="utf-8").read(), "lxml")
    order = [a["href"].split("/")[0] for a in index.select("ul.guides a")]

    for slug in order:
        g = parse_guide(os.path.join(archive, slug, "index.html"))
        bundle = os.path.join(site, "content", "dungeons", slug)
        if os.path.isdir(bundle):
            shutil.rmtree(bundle)
        os.makedirs(os.path.join(bundle, "images"))

        used = [b["image"] for b in g["entrance"] if "image" in b]
        used += [b["image"] for r in g["route"] for b in r["blocks"] if "image" in b]
        used += [b["image"] for b in g["bosses"] if "image" in b]
        for rel in dict.fromkeys(used):
            shutil.copy2(os.path.join(archive, slug, rel), os.path.join(bundle, rel))

        maps = [b["image"] for r in g["route"] for b in r["blocks"] if "image" in b]
        src = manifest.get(slug, {}).get("source", "")
        m = re.search(r"/web/(\d{4})(\d{2})(\d{2})", src)
        front = {
            "title": g["title"],
            "url": f"/{slug}/",
            "expansions": [exp_id],
            "zone": g["zone"],
            "continent": g["continent"],
            "coords": g["coords"],
            "thumbnail": maps[0] if maps else (used[0] if used else ""),
            "entrance": g["entrance"],
            "route": g["route"],
            "bosses": g["bosses"],
            "source": {"url": src, "captured": f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""},
        }
        if manifest.get(slug, {}).get("note"):
            front["archive_note"] = manifest[slug]["note"]
        with open(os.path.join(bundle, "index.md"), "w", encoding="utf-8") as f:
            f.write("---\n" + y_dump(front) + "\n---\n")
        print(f"{slug}: {len(g['route'])} maps, {len(g['bosses'])} bosses, {len(set(used))} images")

    os.makedirs(os.path.join(site, "data", "expansions"), exist_ok=True)
    with open(os.path.join(site, "data", "expansions", f"{exp_id}.yaml"), "w", encoding="utf-8") as f:
        f.write(y_dump({"id": exp_id, "name": exp_name, "guides": order}) + "\n")
    print(f"wrote {len(order)} guides for {exp_name}")


if __name__ == "__main__":
    main()
