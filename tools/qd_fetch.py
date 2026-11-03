#!/usr/bin/env python3
"""Download Quick Dungeon guide pages + images from the Wayback Machine.

Usage: qd_fetch.py OUT_DIR LATEST_TXT SLUG [SLUG ...]
  LATEST_TXT: lines of "<timestamp> /<slug>/" (latest capture per path).
Resumable: files that already exist are skipped.
"""
import gzip, html, json, os, re, socket, sys, time, urllib.error, urllib.request

_gai = socket.getaddrinfo
socket.getaddrinfo = lambda *a, **k: [r for r in _gai(*a, **k) if r[0] == socket.AF_INET]  # IPv4 only


UA = "Mozilla/5.0 (personal archive of quickdungeon.com)"
DELAY = 1.5
WB = "https://web.archive.org/web/{ts}id_/{url}"
UPLOAD_RE = re.compile(r'https?://(?:www\.)?quickdungeon\.com/wp-content/uploads/[^"\'\s<>),&]+', re.I)
CDX = "https://web.archive.org/cdx/search/cdx?url={url}&matchType=exact&fl=timestamp,original&filter=statuscode:200&limit=5"


def cdx_fallback(url):
    """The 2024 site linked lowercased filenames, but the archive often only has the
    original capitalised uploads from ~2016. The CDX index matches case-insensitively,
    so look the path up there and return a fetchable Wayback URL for a real capture."""
    path = re.sub(r"^https?://(www\.)?", "", url)
    # WordPress turned "%E2%80%99" (a curly apostrophe) into a literal "e28099" in some filenames
    variants = [path, re.sub(r"e2(80)(9[89cd])", r"%e2%\1%\2", path)]
    for v in dict.fromkeys(variants):
        data = fetch(CDX.format(url=urllib.request.quote(v, safe="/%")))
        for line in (data or b"").decode(errors="replace").splitlines():
            p = line.split()
            if len(p) == 2:
                return WB.format(ts=p[0], url=p[1])
    return None


def log(*a):
    print(*a, flush=True)


def fetch(url, want_image=False):
    """GET with retries/backoff. Returns bytes or None."""
    waits = [0, 20, 45, 90, 180]
    for i, w in enumerate(waits):
        if w:
            log(f"    retry {i} in {w}s")
            time.sleep(w)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
                ctype = r.headers.get("Content-Type", "")
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            time.sleep(DELAY)
            if want_image and not (ctype.startswith("image/") or data[:3] in (b"\xff\xd8\xff", b"\x89PN", b"GIF")):
                log(f"    not an image ({ctype})")
                return None
            return data
        except urllib.error.HTTPError as e:
            log(f"    HTTP {e.code}")
            if e.code == 404:
                return None
        except Exception as e:  # timeouts, resets
            log(f"    error {type(e).__name__}: {e}")
    return None


def content_block(page):
    """Return the entry-content inner HTML (up to the comments section)."""
    i = page.find('class="entry-content')
    if i < 0:
        return None
    i = page.find(">", i) + 1
    ends = [j for j in (page.find("mh-comments", i), page.find('id="comments"', i),
                        page.find("mh-sidebar", i)) if j > 0]
    j = min(ends) if ends else len(page)
    j = page.rfind("<", i, j)  # back up to the start of the tag holding the marker
    return page[i:j]


def clean(block):
    # Repair <img> tags that WordPress "texturized" into visible text (lost "<", curly quotes),
    # e.g. Balnazzar on stratholme-main-gate:  img class=&#8221;...&#8221; src=&#8221;URL&#8221; ... />
    block = re.sub(r'(?<![<\w])img class=&#8221;([^&]*)&#8221; src=&#8221;(\S+?)&#8221;.*?/>',
                   r'<img class="\1" src="\2" alt="" />', block)
    block = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", "", block)
    block = re.sub(r'\s(srcset|sizes)="[^"]*"', "", block)
    block = re.sub(r'\son\w+="[^"]*"', "", block)
    # drop the closing tags of the entry-content <div> and <article> we cut out of
    block = re.sub(r"(?s)\s*</div>\s*</article>\s*$", "", block)
    return block


PAGE_TMPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} - Quick Dungeon (archive)</title>
<link rel="stylesheet" href="../style.css">
</head><body>
<p class="crumbs"><a href="../index.html">&larr; Classic dungeons</a></p>
<h1>{title}</h1>
<article>
{content}
</article>
<p class="source">Archived from <a href="{src}">{src}</a> (captured {when}).</p>
<script src="../widgets.js"></script>
</body></html>
"""


def main():
    out, latest_path, slugs = sys.argv[1], sys.argv[2], sys.argv[3:]
    ts_for = {}
    for line in open(latest_path):
        p = line.split()
        if len(p) == 2:
            ts_for[p[1].strip("/")] = p[0]
    manifest_path = os.path.join(out, "manifest.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}

    for n, slug in enumerate(slugs, 1):
        ts = ts_for.get(slug, "2024")
        d = os.path.join(out, slug)
        os.makedirs(os.path.join(d, "images"), exist_ok=True)
        page_url = f"https://quickdungeon.com/{slug}/"
        orig = os.path.join(d, "original.html")
        log(f"[{n}/{len(slugs)}] {slug} (ts {ts})")
        if not os.path.exists(orig):
            data = fetch(WB.format(ts=ts, url=page_url))
            if not data:
                log("  PAGE FAILED")
                manifest[slug] = {"status": "page-failed"}
                continue
            open(orig, "wb").write(data)
        page = open(orig, encoding="utf-8", errors="replace").read()
        m = re.search(r"<title>(.*?)</title>", page, re.S)
        title = html.unescape(m.group(1)).split(" – ")[0].strip() if m else slug
        block = content_block(page)
        if block is None:
            log("  no entry-content found")
            manifest[slug] = {"status": "no-content", "title": title}
            continue

        block = clean(block)  # before collecting URLs: drops srcset variants, repairs broken <img>
        urls = sorted(set(u.rstrip(".") for u in UPLOAD_RE.findall(block)))
        images, missing = [], []
        for u in urls:
            name = os.path.basename(u.split("?")[0])
            dest = os.path.join(d, "images", name)
            if not os.path.exists(dest):
                data = fetch(WB.format(ts=ts, url=u), want_image=True)
                if not data:
                    alt = cdx_fallback(u)
                    if alt:
                        log(f"    trying archived variant {alt.rsplit('/', 1)[-1]}")
                        data = fetch(alt, want_image=True)
                if not data:
                    log(f"  missing image {name}")
                    missing.append(u)
                    continue
                open(dest, "wb").write(data)
            images.append(name)
            block = block.replace(u, "images/" + name)
        log(f"  {len(images)} images saved, {len(missing)} missing")

        when = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ts
        src = f"https://web.archive.org/web/{ts}/{page_url}"
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
            PAGE_TMPL.format(title=html.escape(title), content=block, src=src, when=when))
        manifest[slug] = {"status": "ok", "title": title, "source": src, "images": images, "missing": missing}
        json.dump(manifest, open(manifest_path, "w"), indent=2)

    json.dump(manifest, open(manifest_path, "w"), indent=2)
    ok = sum(1 for v in manifest.values() if v.get("status") == "ok")
    miss = sum(len(v.get("missing", [])) for v in manifest.values())
    log(f"DONE: {ok}/{len(slugs)} pages ok, {miss} images missing")


if __name__ == "__main__":
    main()
