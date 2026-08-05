# Freenove ESP32-S3 2.8" (CYD) Display Case — v1.0

A closed, tilted desktop enclosure for the Freenove ESP32-S3 2.8" capacitive-touch
display (ESP32-2432S028R "CYD"). Two printed parts that bolt together with 4 M3 screws.

## Parts

| File | What | Print orientation |
|------|------|-------------------|
| `exports/front_panel.stl` | Lid: LCD window, bevel, mic hole, 4 board standoffs, speaker-grille side | Flat, **screen-face down** |
| `exports/base.stl` | Closed tub: side walls (USB-C mount on the left, speaker mount on the right), full back wall, roof, 2 posts + 2 bosses | **Standing on its back wall** (roof/floor print as vertical walls, no support) |

`case.py` (build123d) generates the real, printable parts into `exports/`. `case.3mf` /
`.glb` are the assembled model; open `viewer.html` (served over localhost) to inspect
it in 3D. Any *test/validation coupon* -- a small carved-out piece printed to check a
fit before committing to a full part -- exports into `exports/coupons/` instead, never
the `exports/` root. `usbc_coupon.py` carves a small test coupon of just the USB-C
mount; `speaker_coupon.py` carves a small test plaque of the speaker retention mount
(ledge + clips + grille).

### Layout

```
case.py, *_coupon.py, viewer.html            CAD source + viewer
README.md, CHANGELOG.md                        docs
exports/           real, printable parts (STL / 3MF / GLB, generated)
exports/coupons/    test/validation coupons only (generated) -- standard convention,
                    keep small fit-test pieces out of the exports/ root
images/     renders & diagrams
photos/     real-world build photos
_incoming/  unsorted uploads to be filed
scratch/    local experiments (gitignored)
```

## Key dimensions

- Panel **105 tall × 87 wide × 3 thick**, LCD window **60 × 46**, tilt **60°** from horizontal
- Board on 4 standoffs (Ø6, 78 × 42 pattern), dropped 3 mm to center the active area
- **Mic** hole Ø2 (chamfered) 6 mm from the top-right mount
- **Speaker** (40.3 × 28.3 × 9.8): sits flush against the **right** side wall over an
  11-slot grille, held by a bottom ledge (shelf + lip) and 2 corner snap clips at the top
- **USB-C** panel-mount on the **left** side wall (wall_R), centered on the wall: 9 × 3
  cutout, 2 holes 15 mm apart
- Assembly: **4 × M3** from the front (2 bottom posts + 2 top bosses), self-tapping

## Printing notes

- Suggested: **3 perimeters**, 15% infill (part is wall-dominated; infill barely matters,
  extra perimeters strengthen the self-tapping screw bosses)
- **`HOLE_COMP = 0.4`** in `case.py` oversizes every screw/mount hole to counter this
  printer's ~0.4 mm hole shrinkage. If screws come out loose lower it; if tight, raise it.
- Regenerate after any change: `python case.py`

## Assembly

1. Slide the speaker onto the base's ledge (right side wall) and press the top edge
   past the 2 corner clips until it snaps in, over the grille.
2. Mount the CYD board on the 4 standoffs.
3. Fit the USB-C panel-mount into the left side wall (2 screws).
4. Seat the panel onto the tub and drive the 4 M3 corner screws from the front.
