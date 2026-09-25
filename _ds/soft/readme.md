# Soft design system

Soft is a light, front-lit interface. There are no separate surface colours:
every card, button and field is made of the ground itself, either **raised**
(a highlight up and to the left, a shade down and to the right) or **pressed**
into it (the same pair turned inward). Contrast comes from light and shade, not
from fills.

## Light and dark

`:root[data-theme="dark"]` swaps the ground and the colours the rest are mixed
from (`--hi-src`, `--lo-src`, the ink sources, `--glow-src`). All of them are
registered, so changing modes eases the whole page across rather than
snapping. Set the mode before the first paint to avoid a flash.

## Tokens

- `--ground` and `--accent` are the only two colours set by hand. Both are
  registered with `@property`, so they can be animated. The site re-tints
  itself by moving them: pick a colour on the gallery wheel and the ground leans
  toward that colour while the accent becomes it.
- Everything else is mixed from them: `--hi` / `--lo` (light and shade),
  `--face` (the raised gradient), `--face-sunk`, and the ink steps (`--ink`,
  `--ink-2`, `--muted`, `--faint`). Never hard-code a surface or text colour,
  or it will stay behind when the environment re-tints.
- Elevation: `--raise-sm/md/lg` to lift, `--press` / `--press-sm` to sink.
  Raised things press in on `:active`.
- Radii: `--radius-sm` 10, `-md` 16, `-lg` 24, `-xl` 30, `-pill`.
- Spacing: `--space-1…8`, on a 4px base.
- Motion: `--ease-out-heavy` is `cubic-bezier(.1, .9, .2, 1)`, a heavy
  ease-out that starts fast and settles slowly with no bounce. It is the curve
  for everything that moves; `--ease-soft` is the same curve under a second name.
  `--retint` is how long a re-tint or a change of mode takes.

## Rules

- Controls are pills or circles. Toggles are a pressed track with a raised
  knob that slides. Tabs are a pressed track with a raised thumb that slides
  to the selected tab.
- Focus is always visible: a 2px accent ring, offset clear of the raised edge.
- Disabled controls lose their shadow and drop to 40% opacity.
- Keep the accent for small marks (kickers, tags, focus, icons on hover),
  never for large areas.

## Files

- `styles.css`: the tokens, the base styles and the `.raised` / `.pressed`
  primitives.
