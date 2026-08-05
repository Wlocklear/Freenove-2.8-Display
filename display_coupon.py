#!/usr/bin/env python3
"""Display-mount fitment coupon: a patch of the FLAT front panel around the 4 board
standoffs (78 x 42 M3 self-tap pattern), the LCD window and the mic hole, carved
from the real panel geometry so it matches the actual mount 1:1.
Print this (screen-face down, like the real panel) to test-fit the CYD board
before committing to the full front panel."""
from build123d import *
import trimesh, os

OUT = os.path.dirname(os.path.abspath(__file__))

# Rebuild the panel exactly as the main script does (front_flat = panel + standoffs,
# top edge already trimmed), then keep only a window around the board mount.
src = open(os.path.join(OUT, "case.py")).read().split("# ── Fuse into exactly TWO")[0]
ns = {"__file__": os.path.join(OUT, "case.py")}
exec(src, ns)
front_flat = ns["front_flat"]

# region: all 4 standoffs + LCD window + mic hole, plus margin
xL, xR, yF, yB = ns["xL"], ns["xR"], ns["yF"], ns["yB"]
STANDOFF_OD = ns["STANDOFF_OD"]
PAD = 6.0

x0, x1 = xL - STANDOFF_OD/2 - PAD, xR + STANDOFF_OD/2 + PAD
y0, y1 = yF - STANDOFF_OD/2 - PAD, yB + STANDOFF_OD/2 + PAD
win = Box(x1 - x0, y1 - y0, 50, align=(Align.MIN, Align.MIN, Align.MIN)
         ).move(Location((x0, y0, -1)))
coupon = front_flat & win

# export
EXP = os.path.join(OUT, "exports", "coupons")   # coupons/test pieces live here, not exports/ root
os.makedirs(EXP, exist_ok=True)
def to_mesh(shape):
    t = os.path.join(EXP, "_t.stl"); export_stl(shape, t); m = trimesh.load(t); os.remove(t); return m
m = to_mesh(coupon)
b = m.bounds
print(f"coupon bounds  x {b[0][0]:.2f}..{b[1][0]:.2f}  y {b[0][1]:.2f}..{b[1][1]:.2f}  z {b[0][2]:.2f}..{b[1][2]:.2f}")
print(f"coupon size    {b[1][0]-b[0][0]:.1f} x {b[1][1]-b[0][1]:.1f} x {b[1][2]-b[0][2]:.1f} mm")
export_stl(coupon, os.path.join(EXP, "display_coupon.stl"))

# also a colored 3mf + glb for the viewer
m.visual.face_colors = [150,150,150,255]
sc = trimesh.Scene(); sc.add_geometry(m, node_name="display_coupon", geom_name="display_coupon")
sc.export(os.path.join(EXP, "display_coupon.3mf"))
sc.export(os.path.join(EXP, "display_coupon.glb"))
print("saved display_coupon.stl / .3mf / .glb")
