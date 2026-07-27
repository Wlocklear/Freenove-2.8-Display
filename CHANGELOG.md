# Changelog

All notable changes to this enclosure are recorded here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/);
versions use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH).

## [1.0.0] — 2026-07-27

First validated release. Two-part bolt-together enclosure for the Freenove
ESP32-S3 2.8" (CYD) display.

### Added
- **Front panel (lid)** — LCD window 60 × 46, chamfered edge, 4 board standoffs
  (Ø6, 78 × 42 pattern, dropped 3 mm), Ø2 chamfered mic hole 6 mm from the
  top-right mount. Leans 60° from horizontal.
- **Base (closed tub)** — side walls following the panel lean, full-height back
  wall with the USB-C panel-mount (9 × 3 cutout, 2 holes 15 mm apart), and a roof.
  Prints standing on its back wall (no support).
- **4-corner M3 mounting** — 2 bottom posts + 2 top bosses, self-tapping, driven
  from the front; verified collinear with the panel holes at the 60° angle.
- **Speaker grille** — 11 slots in the right side wall over the folded cone-face
  patch; speaker taped to the panel back, cone firing out the wall.
- **`HOLE_COMP = 0.4`** — per-printer shrinkage compensation on every screw/mount
  hole so printed sizes match nominal (M3 clearance, self-tap pilots, 3/32" USB-C).
- `usbc_coupon.py` — carves a small USB-C fit-test coupon from the real geometry.

### Notes
- Mic hole and speaker slots do not yet carry `HOLE_COMP`; they will print ~0.4 under.
