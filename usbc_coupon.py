#!/usr/bin/env python3
"""USB-C fitment coupon: a patch of wall_R (the LEFT wall) around the USB-C mount,
carved from the real base geometry so it matches the actual mount 1:1.
Print this small piece to test-fit the module before committing to the full base."""
from build123d import *
import trimesh, os

OUT = os.path.dirname(os.path.abspath(__file__))

# Rebuild the base + usbc_mount exactly as the main script does, then keep only
# a window around the USB-C mount.
src = open(os.path.join(OUT, "case.py")).read().split("# \u2500\u2500 Fuse into exactly TWO")[0]
ns = {"__file__": os.path.join(OUT, "case.py")}
exec(src, ns)
parts = ns["parts"]
# USB-C now lives on wall_R (screen-left); carve the coupon from that
base_asm = (parts["base"] + parts["post_L"] + parts["post_R"]
            + parts["wall_L"] + parts["wall_R"] + parts["wall_back"] + parts["roof"])

# region: a patch of wall_R around the cutout + both screw holes, plus margin
usbc_cx, usbc_cz = ns["usbc_cx"], ns["usbc_cz"]
PANEL_D, WALL_T = ns["PANEL_D"], ns["WALL_T"]
PAD = 6.0

win = Box(ns["USBC_HOLE_DY"]*2 + 2*PAD, WALL_T + 4, ns["USBC_CUT_H"] + 2*PAD,
          align=(Align.CENTER, Align.CENTER, Align.CENTER)
         ).move(Location((usbc_cx, PANEL_D - WALL_T/2, usbc_cz)))
coupon = base_asm & win

# export
EXP = os.path.join(OUT, "exports", "coupons")   # coupons/test pieces live here, not exports/ root
os.makedirs(EXP, exist_ok=True)
def to_mesh(shape):
    t = os.path.join(EXP, "_t.stl"); export_stl(shape, t); m = trimesh.load(t); os.remove(t); return m
m = to_mesh(coupon)
b = m.bounds
print(f"coupon bounds  x {b[0][0]:.2f}..{b[1][0]:.2f}  y {b[0][1]:.2f}..{b[1][1]:.2f}  z {b[0][2]:.2f}..{b[1][2]:.2f}")
print(f"coupon size    {b[1][0]-b[0][0]:.1f} x {b[1][1]-b[0][1]:.1f} x {b[1][2]-b[0][2]:.1f} mm")
export_stl(coupon, os.path.join(EXP, "usbc_coupon.stl"))

# also a colored 3mf + glb for the viewer
m.visual.face_colors = [170,120,210,255]
sc = trimesh.Scene(); sc.add_geometry(m, node_name="usbc_coupon", geom_name="usbc_coupon")
sc.export(os.path.join(EXP, "usbc_coupon.3mf"))
sc.export(os.path.join(EXP, "usbc_coupon.glb"))
print("saved usbc_coupon.stl / .3mf / .glb")
