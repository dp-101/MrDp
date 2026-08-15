"""Generate dist/artifact.html — the single-file copy of the site.

The Artifact host blocks every external request, so this build folds in what
index.html would otherwise fetch: the Nocturne stylesheet, and the gallery's
index plus its thumbnails as data URIs. The web fonts are dropped; the font
stacks already fall back to system-ui.

The result is a preview: its full view shows the 520px thumbnail rather than
the 1600px copy, because embedding those would blow past the size limit.
Run after any change to index.html:

    python tools/build-artifact.py
"""

import base64
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "assets/photos"
LIMIT_MB = 16
STYLESHEET = '<link rel="stylesheet" href="_ds/nocturne-80cf7938-a722-4536-9a1f-d808b619fe64/styles.css">'


def inline_photos():
    """The photo index, with each thumbnail embedded as a data URI."""
    photos = json.loads((PHOTOS / "index.json").read_text(encoding="utf-8"))
    for p in photos:
        raw = (PHOTOS / "thumb" / p["file"]).read_bytes()
        p["thumb"] = "data:image/jpeg;base64," + base64.b64encode(raw).decode("ascii")
    return photos


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")

    css = (ROOT / "_ds/nocturne-80cf7938-a722-4536-9a1f-d808b619fe64/styles.css").read_text(encoding="utf-8")
    css = re.sub(r"@import url\([^)]*\);\s*", "", css, count=1)   # the fonts it pulls
    if STYLESHEET not in html:
        raise SystemExit("index.html no longer links the stylesheet the same way")
    html = html.replace(STYLESHEET, "<style>\n"
                        "/* Nocturne, inlined — generated from _ds/.../styles.css. Do not edit here. */\n"
                        + css + "\n</style>")

    html = re.sub(r'\s*<link rel="preconnect" href="https://fonts\.[^"]*"[^>]*>', "", html)
    html = re.sub(r'\s*<link href="https://fonts\.googleapis\.com[^"]*" rel="stylesheet">', "", html)

    photos = inline_photos()
    html = html.replace("</head>",
                        "<script>window.__PHOTOS__ = "
                        + json.dumps(photos, separators=(",", ":"))
                        + ";</script>\n</head>")

    out = ROOT / "dist/artifact.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")

    size = out.stat().st_size / 1024 / 1024
    print(f"{out.relative_to(ROOT)}  {size:.1f} MB  ({len(photos)} photographs inlined)")
    if size > LIMIT_MB:
        raise SystemExit(f"over the {LIMIT_MB} MB artifact limit — shrink the thumbnails")


if __name__ == "__main__":
    main()
