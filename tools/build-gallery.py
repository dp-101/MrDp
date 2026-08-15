"""Build the gallery's web assets from the photo drop in gal/.

Reads every JPEG in gal/, writes a thumbnail and a display copy into
assets/photos/, and records each photo's capture date and dominant colour in
assets/photos/index.json — the two things the gallery sorts on.

The originals in gal/ are only ever read; they are not committed (see
.gitignore). Re-run after adding photos:

    python tools/build-gallery.py

Positions on the colour wheel run white -> violet -> blue -> green -> yellow
-> red -> black -> grey -> back to white, matching the wheel drawn in the UI:
the rainbow with white at its violet end, black at its red end, and grey
bridging the two.
"""

import json
import pathlib
import colorsys
from PIL import Image, ImageOps

SRC = pathlib.Path("gal")
OUT = pathlib.Path("assets/photos")
THUMB_EDGE = 520        # grid
VIEW_EDGE = 1600        # full view
ANALYSIS_EDGE = 160     # colour sampling

# A pixel only votes on hue if it is colourful enough and neither crushed
# black nor blown white.
MIN_SAT = 0.18
MIN_VAL = 0.10
MAX_VAL = 0.97
# Below this share of colourful pixels the photo is treated as neutral.
NEUTRAL_CUTOFF = 0.20

# (upper bound in degrees, name) — walked in order. The yellow/green line
# sits at 62 rather than the textbook 70: foliage peaks in the olives, and
# above 62 a photo reads green to the eye even when its hue says yellow.
HUE_NAMES = [
    (12,  "red"),
    (40,  "orange"),
    (62,  "yellow"),
    (155, "green"),
    (200, "cyan"),
    (250, "blue"),
    (295, "violet"),
    (340, "pink"),
    (360, "red"),
]

# The wheel the UI draws, clockwise: the rainbow, then white, grey and black
# closing the circle back to red — white next to the blues, black next to
# the reds, grey bridging the two.
WHEEL = ["red", "orange", "yellow", "green", "cyan", "blue",
         "violet", "pink", "white", "grey", "black"]


def capture_date(img):
    """EXIF DateTimeOriginal as YYYY-MM-DD HH:MM, or None."""
    exif = img.getexif()
    raw = exif.get_ifd(0x8769).get(36867) or exif.get(306)
    if not raw:
        return None
    try:
        d, t = str(raw).split(" ")
        return d.replace(":", "-") + " " + t[:5]
    except ValueError:
        return None


def hue_name(hue):
    lo = 0
    for bound, name in HUE_NAMES:
        if hue < bound:
            return name, (hue - lo) / max(bound - lo, 1)
        lo = bound
    return "red", 0.0


def wheel_position(name, within):
    """One sortable number: which wheel segment, and where inside it."""
    return round(WHEEL.index(name) + min(max(within, 0.0), 0.999), 4)


def analyse(img):
    """Dominant colour of a photo, as a wheel position and a name."""
    small = img.convert("RGB").copy()
    small.thumbnail((ANALYSIS_EDGE, ANALYSIS_EDGE), Image.Resampling.BILINEAR)

    bins = [0.0] * 36
    colourful = 0
    total = 0
    val_sum = 0.0
    best = (0.0, (0, 0, 0))

    raw = small.tobytes()
    for i in range(0, len(raw), 3):
        r, g, b = raw[i], raw[i + 1], raw[i + 2]
        total += 1
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        val_sum += v
        if s >= MIN_SAT and MIN_VAL <= v <= MAX_VAL:
            colourful += 1
            weight = s * v
            bins[int(h * 360) // 10] += weight
            if weight > best[0]:
                best = (weight, (r, g, b))

    share = colourful / max(total, 1)
    mean_val = val_sum / max(total, 1)

    if share < NEUTRAL_CUTOFF:
        # Neutral: placed on the white -> grey -> black arc by brightness,
        # which is the direction the wheel runs.
        if mean_val < 0.28:
            name = "black"
        elif mean_val > 0.68:
            name = "white"
        else:
            name = "grey"
        return {
            "family": "neutral", "colour": name, "tone": round(mean_val, 3),
            "wheel": wheel_position(name, 1.0 - mean_val),
            "swatch": "#%02x%02x%02x" % tuple(round(mean_val * 255) for _ in range(3)),
        }

    # Smooth the histogram around the circle so a hue straddling two bins
    # does not lose to a narrow spike.
    smooth = [bins[(i - 1) % 36] * 0.5 + bins[i] + bins[(i + 1) % 36] * 0.5
              for i in range(36)]
    peak = max(range(36), key=lambda i: smooth[i])
    hue = peak * 10 + 5
    name, within = hue_name(hue)

    return {
        "family": "colour", "colour": name, "hue": hue,
        "wheel": wheel_position(name, within),
        "swatch": "#%02x%02x%02x" % best[1],
    }


def derivative(img, edge, path, quality):
    copy = img.copy()
    copy.thumbnail((edge, edge), Image.Resampling.LANCZOS)
    copy.save(path, "JPEG", quality=quality, optimize=True, progressive=True)
    return copy.size


def reindex():
    """Re-run only the colour analysis, off the thumbnails already built.

    Dates and dimensions are kept from the existing index, so tuning the
    colour rules costs seconds instead of re-encoding every photo.
    """
    index = OUT / "index.json"
    photos = json.loads(index.read_text(encoding="utf-8"))
    for p in photos:
        thumb = Image.open(OUT / "thumb" / p["file"])
        for key in ("family", "colour", "hue", "tone", "wheel", "arc", "swatch"):
            p.pop(key, None)
        p.update(analyse(thumb))
    photos.sort(key=lambda p: p["date"] or "")
    index.write_text(json.dumps(photos, separators=(",", ":")), encoding="utf-8")
    print(f"re-analysed {len(photos)} photos -> {index}")


def main():
    (OUT / "thumb").mkdir(parents=True, exist_ok=True)
    (OUT / "view").mkdir(parents=True, exist_ok=True)

    photos = []
    files = sorted(SRC.glob("*.jpg")) + sorted(SRC.glob("*.jpeg"))
    for i, f in enumerate(files, 1):
        img = Image.open(f)
        date = capture_date(img)
        img.draft("RGB", (VIEW_EDGE * 2, VIEW_EDGE * 2))   # fast JPEG scaling
        img = ImageOps.exif_transpose(img).convert("RGB")

        name = f.stem + ".jpg"
        derivative(img, VIEW_EDGE, OUT / "view" / name, 82)
        tw, th = derivative(img, THUMB_EDGE, OUT / "thumb" / name, 78)

        entry = {"file": name, "w": tw, "h": th, "date": date}
        entry.update(analyse(img))
        photos.append(entry)
        print(f"[{i:>3}/{len(files)}] {name}  {entry['colour']:<7} {date}")

    photos.sort(key=lambda p: p["date"] or "")
    (OUT / "index.json").write_text(
        json.dumps(photos, indent=None, separators=(",", ":")), encoding="utf-8")
    print(f"\n{len(photos)} photos -> {OUT/'index.json'}")


if __name__ == "__main__":
    import sys
    reindex() if "--reindex" in sys.argv else main()
