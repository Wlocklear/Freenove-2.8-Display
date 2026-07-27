# Freenove ESP32-S3 2.8" (CYD) Display Case — v1.0

A closed, tilted desktop enclosure for the Freenove ESP32-S3 2.8" capacitive-touch
display (ESP32-2432S028R "CYD"). Two printed parts that bolt together with 4 M3 screws.

## Parts

| File | What | Print orientation |
|------|------|-------------------|
| `front_panel.stl` | Lid: LCD window, bevel, mic hole, 4 board standoffs, speaker-grille side | Flat, **screen-face down** |
| `base.stl` | Closed tub: side walls, full back wall (USB-C mount), roof, 2 posts + 2 bosses | **Standing on its back wall** (roof/floor print as vertical walls, no support) |

`base_plate.py` (build123d) generates everything. `base_plate.3mf` / `.glb` are the
assembled model; open `viewer.html` (served over localhost) to inspect it in 3D.
`usbc_coupon.py` carves a small test coupon of just the USB-C mount for fit checks.

## Key dimensions

- Panel **105 tall × 87 wide × 3 thick**, LCD window **60 × 46**, tilt **60°** from horizontal
- Board on 4 standoffs (Ø6, 78 × 42 pattern), dropped 3 mm to center the active area
- **Mic** hole Ø2 (chamfered) 6 mm from the top-right mount
- **Speaker** (40.4 × 28.1 × 10): thin side taped to the panel back, cone fires out an
  11-slot grille in the **right** side wall
- **USB-C** panel-mount in the back wall: 9 × 3 cutout, 2 holes 15 mm apart
- Assembly: **4 × M3** from the front (2 bottom posts + 2 top bosses), self-tapping

## Printing notes

- Suggested: **3 perimeters**, 15% infill (part is wall-dominated; infill barely matters,
  extra perimeters strengthen the self-tapping screw bosses)
- **`HOLE_COMP = 0.4`** in `base_plate.py` oversizes every screw/mount hole to counter this
  printer's ~0.4 mm hole shrinkage. If screws come out loose lower it; if tight, raise it.
- Regenerate after any change: `python base_plate.py`

## Assembly

1. Tape the speaker to the panel back (right side), cone toward the side-wall grille.
2. Mount the CYD board on the 4 standoffs.
3. Fit the USB-C panel-mount into the back wall (2 screws).
4. Seat the panel onto the tub and drive the 4 M3 corner screws from the front.
