#!/usr/bin/env python3
"""USB-C fitment coupon: the USB-C wall + a patch of the base floor around it,
carved from the real base geometry so it matches the actual mount 1:1.
Print this small piece to test-fit the module before committing to the full base."""
from build123d import *
import trimesh, os

OUT = r"C:\Users\wlock\GitHub\3D Prints\Freenove_ESP32S3_2.8_Display_Case"

# Rebuild the base + usbc_mount exactly as the main script does, then keep only
# a window around the USB-C mount (with a slab of floor extending inward).
src = open(os.path.join(OUT, "base_plate.py")).read().split("# \u2500\u2500 Fuse into exactly TWO")[0]
ns = {}
exec(src, ns)
parts = ns["parts"]
# USB-C now lives in the full back wall (enclosure); carve the coupon from that
base_asm = (parts["base"] + parts["post_L"] + parts["post_R"]
            + parts["wall_L"] + parts["wall_R"] + parts["wall_back"] + parts["roof"])

# region: full wall (y 22.5..52.5, back edge x=52.45) + FLOOR_KEEP mm of floor inward
usbc_x  = ns["panel_min_x"] + ns["BASE_LEN"]      # back edge x
cy      = ns["PLATE_D"] / 2                        # 37.5
FLOOR_KEEP = 18.0                                  # how much floor to include, inward from the wall
PAD_Y      = 4.0                                   # margin each side of the 30mm wall

win = Box(FLOOR_KEEP + ns["USBC_T"] + 1, ns["USBC_W"] + 2*PAD_Y, 40,
          align=(Align.MAX, Align.CENTER, Align.MIN)
          ).move(Location((usbc_x + 0.5, cy, -1)))
coupon = base_asm & win

# export
EXP = os.path.join(OUT, "exports")
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
