#!/usr/bin/env python3
"""Freenove Speaker Coupon -- speaker retention-clip fitment test piece.

Real speaker (measured off the kit): 40.3mm long x 28.3mm wide x 9.8mm deep --
NOT square. It sits flush against the RIGHT side wall, over the grille, in the
SAME tilted orientation as the grille slots themselves -- built directly in the
panel's local (pre-tilt) frame and folded into place with case.py's own fold(),
exactly like the grille cut is, so it's guaranteed to land on solid wall.

Retention is a shelf, not a box of corner tabs:
  - a LEDGE at the BOTTOM of the grille, sized to the speaker's width x depth,
    with a small lip -- the speaker rests on it like a shelf.
  - 2 corner flex-clips at the TOP (split to clear the speaker's wire, which
    exits the middle) that snap over the top edge.

This geometry is now folded into case.py's real wall_L for the actual build.
This script instead carves a small, quick-printing standalone plaque (a plain
rectangle, not the real wall's shape) with the same ledge + clip + grille, for
fit-testing before/after tweaking the numbers here (then mirror any change
into case.py's "Speaker retention mount" section).
"""
from build123d import *
import trimesh, os

OUT = os.path.dirname(os.path.abspath(__file__))

src = open(os.path.join(OUT, "case.py")).read().split("# ── Fuse into exactly TWO")[0]
ns = {"__file__": os.path.join(OUT, "case.py")}
exec(src, ns)
fold = ns["fold"]
PANEL_T, x_bot, WALL_T = ns["PANEL_T"], ns["x_bot"], ns["WALL_T"]
SPK_FROM_BOTTOM, SPK_H_grille = ns["SPK_FROM_BOTTOM"], ns["SPK_H"]
SPK_DEPTH, SPK_SLOT_INSET = ns["SPK_DEPTH"], ns["SPK_SLOT_INSET"]
SPK_SLOT_PITCH, SPK_SLOT_W = ns["SPK_SLOT_PITCH"], ns["SPK_SLOT_W"]

# ── real speaker, as measured off the kit ─────────────────────────────────────
SPK_L, SPK_W, SPK_THK = 40.3, 28.3, 9.8     # long x wide x deep (mm) -- NOT square
CLR = 1.3                                     # fit clearance around the speaker (+1mm -- it
                                               # wasn't clipping in with the old 0.3mm)

# panel-local frame (matches how case.py builds the grille cuts, pre-fold/pre-tilt):
#   X = px  (length, up/down the panel's slope -- larger px = physically lower)
#   Y = py  (wall-normal direction -- speaker thickness sticks out this way)
#   Z = pz  (width, across the wall -- the same axis SPK_DEPTH already uses)
px_bot = x_bot - SPK_FROM_BOTTOM
px_top = px_bot - SPK_L
# pz0=PANEL_T sits EXACTLY on the wall's sloped front edge -- and that edge is the SEAM the
# front panel physically seats against when assembled. Flush there means the speaker collides
# with the panel. The one shift: pull it 4mm off that edge, into the wall, clear of the seam.
PZ_SHIFT = 4.0
pz0, pz1 = PANEL_T + PZ_SHIFT, PANEL_T + PZ_SHIFT + SPK_W    # speaker's width footprint
Y0 = WALL_T                              # wall's inner (interior-facing) face
YS = Y0                                    # speaker sits flush against the grille wall, no standoff

# ── ledge: a shelf at the bottom of the grille, sized to the speaker's width x depth,
#    with a small retaining lip -- the speaker rests on it. It's solid from the wall
#    face (Y0) out past the speaker (YS+SPK_THK), so it also forms the standoff riser ──
LEDGE_T   = 3.5     # shelf structural thickness (px direction)
LIP_H     = 1.5      # retaining lip height (px direction), rises above the shelf surface
LIP_REACH = 1.5        # lip overhang (py), inward over the speaker's outer-bottom edge
WELD      = 0.3          # sinks into the wall for a true fused union

# NOTE: Box(px_extent, py_extent, pz_extent).move(Location((px, py, pz))) throughout --
# matching case.py's own convention for its (pre-fold) grille-slot cut boxes.
shelf = Box(LEDGE_T + WELD, (YS + SPK_THK + CLR) - Y0, pz1 - pz0, align=(Align.MIN, Align.MIN, Align.MIN)
           ).move(Location((px_bot, Y0, pz0)))
lip = Box(LIP_H, LIP_REACH, pz1 - pz0, align=(Align.MIN, Align.MIN, Align.MIN)
         ).move(Location((px_bot - LIP_H, YS + SPK_THK + CLR - LIP_REACH, pz0)))
ledge = shelf + lip

# ── top clip: TWO flex tabs at the corners (not one in the middle) -- the speaker's wire
#    exits from the middle of the top edge, so a centered clip would land right on it.
#    Each is solid from the wall face out past the speaker, bridging the standoff gap ────
CLIP_W       = 8.0      # each tab's width (pz direction)
CLIP_MARGIN  = 3.0        # inset from the pz0/pz1 corners
CLIP_POST    = 1.6          # flex post thickness (px direction), thin so it flexes on insertion
CLIP_REACH   = 2.0            # lip overhang (px), into the speaker's top face
CLIP_LIP_H   = 1.6              # lip height (py)
CHAM         = 0.8                # lead-in chamfer on the lip's underside-inner edge

def top_clip(cz0, cz1):
    post = Box(CLIP_POST, (YS + SPK_THK + CLR + WELD) - (Y0 - WELD), cz1 - cz0,
               align=(Align.MIN, Align.MIN, Align.MIN)
              ).move(Location((px_top - CLIP_POST, Y0 - WELD, cz0)))
    tab_lip = Box(CLIP_POST + CLIP_REACH, CLIP_LIP_H, cz1 - cz0, align=(Align.MIN, Align.MIN, Align.MIN)
                 ).move(Location((px_top - CLIP_POST, YS + SPK_THK + CLR, cz0)))
    tab = post + tab_lip
    # lead-in chamfer on the lip's bottom-inner edge (the one the speaker cams against)
    lead_x = px_top + CLIP_REACH
    lead = ShapeList([e for e in tab.edges()
                       if abs(e.center().Y - (YS + SPK_THK + CLR)) < 1e-3
                       and abs(e.center().X - lead_x) < 1e-3])
    if lead:
        tab = chamfer(lead, CHAM)
    return tab

clip_tab = (top_clip(pz0 + CLIP_MARGIN, pz0 + CLIP_MARGIN + CLIP_W)
            + top_clip(pz1 - CLIP_MARGIN - CLIP_W, pz1 - CLIP_MARGIN))

# ── plain rectangular wall patch (NOT the real wall_L's trapezoid silhouette) sized just
#    around the mounts, with the same grille slots case.py cuts -- built directly in the
#    panel-local frame, right alongside the ledge/clip, then folded together as one piece ──
PAD = 3.0
slab_x0 = min(px_top - CLIP_POST - 4, px_top) - PAD
slab_x1 = max(px_bot + LEDGE_T + 2, px_bot) + PAD
slab_z0, slab_z1 = pz0 - PAD, pz1 + PAD
wall_patch = Box(slab_x1 - slab_x0, WALL_T, slab_z1 - slab_z0, align=(Align.MIN, Align.MIN, Align.MIN)
                 ).move(Location((slab_x0, 0, slab_z0)))

# same slot size/count/spacing as case.py's grille cut, but CENTERED on the mount footprint
# (px_top..px_bot, pz0..pz1) instead of case.py's own offset -- not on the wall's original spot
_spk_zc = (pz0 + pz1) / 2
_slot_len = min(SPK_DEPTH - 2 * SPK_SLOT_INSET, (pz1 - pz0) - 2 * SPK_SLOT_INSET)
_n = int(SPK_H_grille // SPK_SLOT_PITCH)
_start = (px_top + px_bot) / 2 + (_n - 1) * SPK_SLOT_PITCH / 2
for _i in range(_n):
    _sx = _start - _i * SPK_SLOT_PITCH
    if slab_x0 <= _sx <= slab_x1:
        _cut = Box(SPK_SLOT_W, WALL_T + 4, _slot_len, align=(Align.CENTER, Align.CENTER, Align.CENTER)
                  ).move(Location((_sx, WALL_T / 2, _spk_zc)))
        wall_patch = wall_patch - _cut

# fold the whole thing (wall patch + ledge + clip) into world space together, one piece
coupon = fold(wall_patch + ledge + clip_tab)

# rest flat on the print bed
b = coupon.bounding_box()
coupon = coupon.move(Location((0, -b.min.Y, 0)))

# ── export ──────────────────────────────────────────────────────────────────
EXP = os.path.join(OUT, "exports", "coupons")   # coupons/test pieces live here, not exports/ root
os.makedirs(EXP, exist_ok=True)
def to_mesh(shape):
    t = os.path.join(EXP, "_t.stl"); export_stl(shape, t); m = trimesh.load(t); os.remove(t); return m

NAME = "Freenove_Speaker_Coupon"
export_stl(coupon, os.path.join(EXP, f"{NAME}.stl"))
cb = coupon.bounding_box()
print(f"{NAME} size  {cb.max.X-cb.min.X:.1f} x {cb.max.Y-cb.min.Y:.1f} x {cb.max.Z-cb.min.Z:.1f} mm")
print(f"speaker footprint (panel-local)  px [{px_top:.2f},{px_bot:.2f}]  pz [{pz0:.2f},{pz1:.2f}]")
print(f"solids in coupon (should be 1): {len(coupon.solids())}")

m_coupon = to_mesh(coupon); m_coupon.visual.face_colors = [170, 120, 210, 255]
sc = trimesh.Scene()
sc.add_geometry(m_coupon, node_name=NAME, geom_name=NAME)
sc.export(os.path.join(EXP, f"{NAME}.3mf"))
sc.export(os.path.join(EXP, f"{NAME}.glb"))
print(f"saved {NAME}.stl + .3mf/.glb")
