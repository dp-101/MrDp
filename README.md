# MrDp

A one-screen portfolio — Work, Writing and Gallery open as an expanding panel over the
homepage rather than as separate pages. Built on the **Nocturne** design system: a dark
blue-grey ground, a single blurple accent used as line and glow, and no flat saturated fills.

**Live:** [dp-101.github.io/MrDp](https://dp-101.github.io/MrDp/)

## Layout

```text
index.html      the site — static HTML, one <style> block, ~120 lines of vanilla JS
.nojekyll       stops GitHub Pages' Jekyll from skipping _ds/ (paths starting with _)
_ds/nocturne-…  the design system: tokens, ramps and component classes
  styles.css      the only stylesheet; every color, space and radius comes from here
  readme.md       how the system is meant to be used
src/            the design-tool source this site was ported from
  MrDp Portfolio.dc.html    the original component
  support.js, image-slot.js its runtime
dist/artifact.html          generated copy with the CSS inlined — do not edit by hand
```

No build step, no dependencies, no package manager. Open `index.html` and it runs.

## Running it locally

```sh
python -m http.server 8000
# then open http://localhost:8000/
```

Opening the file directly with `file://` works too, though the stylesheet path is
easier to reason about when it is served.

## Editing

- **Colors, spacing, radii, shadows** — change the tokens at the top of
  `_ds/nocturne-…/styles.css`. Nothing in `index.html` hardcodes a value the tokens
  already carry, apart from the three local surfaces (`--card`, `--card-hover`,
  `--panel`) declared at the top of its `<style>` block.
- **Content** — Work rows, Writing entries and Gallery captions are plain markup inside
  `#panelBody` in `index.html`.
- **Gallery photographs** — each `.frame` is an empty composed frame. Drop an
  `<img src="assets/gallery/….jpg" alt="…">` inside one to fill it; `mix-blend-mode:
  lighten` is already applied, so photographs shot on dark backgrounds blend into the
  page. Prefer dark or black backgrounds, per the Nocturne guidance.
- **After changing `index.html`**, regenerate `dist/artifact.html` — it is the same page
  with `styles.css` inlined, for hosts that block external requests.

## Notes

- The Work and Writing entries are sample content and read as placeholders until real
  ones replace them.
- `src/` is kept so the original component still opens in the design tool; it is not
  served and nothing on the live site depends on it.
