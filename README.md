# MrDp

A one-screen portfolio — Gallery and Work open as an expanding panel over the
homepage rather than as separate pages. Built on the **Nocturne** design system: a dark
blue-grey ground, a single blurple accent used as line and glow, and no flat saturated fills.

**Live:** [dp-101.github.io/MrDp](https://dp-101.github.io/MrDp/)

## Layout

```text
index.html      the site — static HTML, one <style> block, vanilla JS
.nojekyll       stops GitHub Pages' Jekyll from skipping _ds/ (paths starting with _)
_ds/nocturne-…  the design system: tokens, ramps and component classes
  styles.css      the only stylesheet; every color, space and radius comes from here
  readme.md       how the system is meant to be used
assets/photos/  generated — the gallery's web copies and its index
  thumb/          520px, for the grid
  view/           2400px, for the full view and its zoom
  index.json      each photo's timeline position and dominant colour
tools/          the two build scripts (Python + Pillow)
src/            the design-tool source this site was ported from
dist/artifact.html   generated single-file copy — do not edit by hand
gal/            your photo originals — read by the build, never committed
```

The site itself has no build step and no dependencies. The two scripts under `tools/`
only run when the photographs change.

## Running it locally

```sh
python -m http.server 8000
# then open http://localhost:8000/
```

Serve it rather than opening the file directly — the gallery fetches `index.json`,
which `file://` blocks.

## The gallery

86 photographs, arranged two ways over the same set:

- **Timeline** — by the capture date read out of each photo's EXIF at build time.
  The arrow flips between oldest and newest first.
- **Colour** — by dominant colour, placed around a wheel that runs the rainbow, then
  white, grey and black closing the circle back into red. The arrow reverses it, and
  picking a wedge shows only that colour.

A photograph's colour is whichever hue holds the majority of its frame, weighted so
that washed-out and near-black pixels do not vote. Photographs with no real hue —
night shots, silhouettes — fall onto the white/grey/black part of the wheel by
brightness.

### Adding photographs

Drop them into `gal/` and run:

```sh
python tools/build-gallery.py     # resize + read dates + classify colour
python tools/build-artifact.py    # refresh the single-file copy
```

`build-gallery.py` writes both derivative sizes and `index.json`; nothing in
`index.html` needs editing. Tuning the colour rules alone is cheaper — pass
`--reindex` to re-classify from the existing thumbnails instead of re-encoding
everything.

No capture date reaches the published site. The index carries only the resulting
timeline position, derivatives are named from a hash of the original rather than
from the camera's dated filename, and re-encoding drops the EXIF.

Originals stay in `gal/`, which is gitignored: 86 phone photographs are 284 MB, and
the committed web copies are 45 MB.

The grid holds its photographs back until the card has finished opening — laying
out and decoding 86 of them mid-animation is what made the expansion stutter.
They wait at the middle of the card's bottom edge and fan out from there, and the
thumbnails are warmed on idle from the home screen so opening is a layout, not a
download.

## Editing

- **Colors, spacing, radii, shadows** — change the tokens at the top of
  `_ds/nocturne-…/styles.css`. Nothing in `index.html` hardcodes a value the tokens
  already carry, apart from the three local surfaces (`--card`, `--card-hover`,
  `--panel`) declared at the top of its `<style>` block.
- **Content** — the Work rows are plain markup inside `#panelBody` in `index.html`.
- **After changing `index.html`**, run `python tools/build-artifact.py`.

## Notes

- The Work entries are sample content and read as placeholders until real ones
  replace them.
- `dist/artifact.html` is a preview build for hosts that block external requests: it
  carries the stylesheet and all 86 thumbnails inline, so its full view shows the
  520px copy rather than the 2400px one, and zooming it will look soft.
- `src/` is kept so the original component still opens in the design tool; it is not
  served and nothing on the live site depends on it.
