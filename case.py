#!/usr/bin/env python3
"""
Freenove ESP32-S3 2.8" (CYD) Display Case  --  v1.0
TWO SEPARATE PARTS (print apart, bolt together).
  front_panel : screen panel (LCD window, bevel, mic hole, 4 board standoffs) + speaker
                grille footprint; 4 M3 clearance holes at the corners. Leans at TILT deg.
  base        : closed tub -- side walls + full back wall + roof; its front edge follows
                the panel lean; 2 bottom posts + 2 top bosses (M3 self-tap); speaker
                retention mount (ledge + 2 corner clips) on wall_L, over the grille;
                USB-C panel mount on wall_R (screen-LEFT), centered on the wall.
Assembly: 4 M3 screws from the FRONT (panel corners) into the base posts/bosses.
Print: front_panel flat (screen down); base STANDING ON ITS BACK WALL (no support).
Hole sizes carry a per-printer shrinkage comp (HOLE_COMP).
"""
from build123d import *
import trimesh, os, math

# ── Front panel (screen) ─────────────────────────────────────────────────────
PANEL_W, PANEL_D, PANEL_T = 100.0, 87.0, 3.0   # width widened +6/side (75->87) for the speaker
LCD_W, LCD_H, BEVEL = 60.0, 46.0, 0.6
STANDOFF_H, STANDOFF_OD, STANDOFF_HOLE = 3.3, 6.0, 2.8
SPACING_X, SPACING_Y = 78.0, 42.0
BOARD_DROP = 3.0           # shift the 4 board standoffs toward the panel bottom (+x local)
MIC_D  = 2.0               # mic hole diameter
MIC_CHAM = 0.6             # 45deg chamfer on the SCREEN-side entry so it prints open
MIC_DY = 6.0               # mic hole offset from the top-right mount, center-to-center
                           # (+y local = screen-LEFT when viewed from the front)

# ── Speaker grille (RIGHT side wall) ─────────────────────────────────────────
# Speaker taped to the panel back (thin 40.4x10 face); cone (40.4x28.1) faces the
# RIGHT side wall, so the grille lands as a tilted patch on that wall.
SPK_H          = 40.4      # speaker height, along the panel length (local x)
SPK_DEPTH      = 28.1      # cone-face depth into the enclosure (local z from panel back)
SPK_FROM_BOTTOM = 30.0     # speaker BOTTOM edge, up from the panel bottom edge
SPK_SLOT_W     = 1.6       # grille slot width (along the panel length)
SPK_SLOT_PITCH = 3.6       # slot spacing
SPK_SLOT_INSET = 4.0       # inset of slot length within the 28.1 depth

# ── Speaker retention mount (on wall_L, over the grille) ─────────────────────
# Real speaker, as measured off the kit: 40.3 x 28.3 x 9.8mm -- NOT square. It mounts
# flush against wall_L's inner face, level with the grille, held by a bottom ledge
# (shelf + lip) and 2 corner snap clips at the top (split to clear the speaker's wire,
# which exits the middle). Validated as speaker_coupon.py before folding in here.
SPK_MNT_W, SPK_MNT_THK = 28.3, 9.8   # speaker width x thickness (SPK_H above is its length)
SPK_MNT_CLR      = 1.3                 # fit clearance around the speaker
SPK_MNT_PZ_SHIFT = 4.0                   # local-z sits on the panel's seat seam at 0 -- clear it
SPK_LEDGE_T, SPK_LIP_H, SPK_LIP_REACH = 3.5, 1.5, 1.5   # bottom ledge: thickness, lip height/reach
SPK_CLIP_W, SPK_CLIP_MARGIN = 8.0, 3.0                    # top clips: width, inset from corners
SPK_CLIP_POST, SPK_CLIP_REACH = 1.6, 2.0                    # top clips: flex post, lip reach
SPK_CLIP_LIP_H, SPK_CLIP_CHAM = 1.6, 0.8                      # top clips: lip height, lead-in chamfer

TILT = 60.0

# ── Bottom-corner M3 connection (2 screws) ───────────────────────────────────
BOTTOM_EXT = 5.0           # extra panel below the board so it clears the posts
BOLT_YS  = (8.0, PANEL_D - 8.0)   # local y of the 2 corner screws (8mm from each edge, any width)
PANEL_CLR = 3.4            # M3 clearance in the panel (NOMINAL; HOLE_COMP added at cut)
POST_OD   = 12.0           # base post diameter
POST_PILOT = 2.5           # M3 self-tap pilot in the post (NOMINAL; HOLE_COMP added at cut)

# FDM shrinkage compensation: this printer prints holes ~0.4mm under. Added to every
# screw/mount hole DIAMETER so the printed size matches the nominal above. Tune to taste:
# if screws end up loose, lower it; if still tight, raise it.
HOLE_COMP = 0.4

# ── USB-C panel mount, centered on the LEFT wall (wall_R, screen-left) ────────
USBC_W, USBC_H, USBC_T = 30.0, 10.0, 3.0   # mount block: wide(y), tall(z), thick(x)
USBC_CUT_W, USBC_CUT_H = 9.0, 3.0          # cutout for the connector shell
USBC_HOLE_D  = 2.38                        # screw clearance holes (3/32")
USBC_HOLE_DY = 7.5                         # hole center from cutout center (15mm apart)
USBC_MOD_H   = 6.8                         # module height; it rests on the base top face

OUT = os.path.dirname(os.path.abspath(__file__))
# ──────────────────────────────────────────────────────────────────────────────
cx, cy = 0.0, PANEL_D/2
x_top, x_bot = -PANEL_W/2, PANEL_W/2 + BOTTOM_EXT   # board stays centered; extra at bottom
BOLT_X = x_bot - 5.0                                 # screws just up from the new bottom edge
TOP_BOLT_X = x_top + 6.0                              # matching screws just below the top edge

# ---- front panel (flat, local frame; screen face = z0, standoffs on z=PANEL_T) ----
panel_box = Box(x_bot - x_top, PANEL_D, PANEL_T, align=(Align.MIN, Align.MIN, Align.MIN)).move(Location((x_top, 0, 0)))
window = Box(LCD_W, LCD_H, PANEL_T + 2, align=(Align.CENTER, Align.CENTER, Align.CENTER))
front  = panel_box - window.move(Location((cx, cy, PANEL_T/2)))
if BEVEL > 0:
    z0 = front.edges().group_by(Axis.Z)[0]
    def _win(e):
        x, y = e.center().X, e.center().Y - cy
        return (abs(abs(x) - LCD_W/2) < 0.5 and abs(y) < LCD_H/2 + 0.5) or \
               (abs(abs(y) - LCD_H/2) < 0.5 and abs(x) < LCD_W/2 + 0.5)
    front = chamfer(ShapeList([e for e in z0 if _win(e)]), BEVEL)
for bx in (BOLT_X, TOP_BOLT_X):     # 4 M3 clearance holes: bottom + top corners
    for by in BOLT_YS:
        front = front - Cylinder((PANEL_CLR+HOLE_COMP)/2, PANEL_T + 2, align=(Align.CENTER, Align.CENTER, Align.CENTER)
                                 ).move(Location((bx, by, PANEL_T/2)))

def standoff(x, y):
    p = Cylinder(STANDOFF_OD/2, STANDOFF_H, align=(Align.CENTER, Align.CENTER, Align.MIN)).move(Location((x, y, PANEL_T)))
    return p - Cylinder(STANDOFF_HOLE/2, STANDOFF_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN)).move(Location((x, y, PANEL_T)))
board_cx = cx + BOARD_DROP                  # board center, dropped toward the panel bottom
xL, xR = board_cx - SPACING_X/2, board_cx + SPACING_X/2
yF, yB = cy - SPACING_Y/2, cy + SPACING_Y/2

# ---- mic hole: MIC_DY screen-left of the top-right board mount (xL, yF), same height ----
mic_x, mic_y = xL, yF + MIC_DY
front = front - Cylinder(MIC_D/2, PANEL_T + 2, align=(Align.CENTER, Align.CENTER, Align.CENTER)
                         ).move(Location((mic_x, mic_y, PANEL_T/2)))
if MIC_CHAM > 0:        # funnel the z=0 (screen) face out to MIC_D + 2*MIC_CHAM
    front = front - Cone(MIC_D/2 + MIC_CHAM, MIC_D/2, MIC_CHAM,
                         align=(Align.CENTER, Align.CENTER, Align.MIN)
                         ).move(Location((mic_x, mic_y, 0)))

parts = {
    "front_panel": front,
    "standoff_FL": standoff(xL, yF), "standoff_FR": standoff(xR, yF),
    "standoff_BL": standoff(xL, yB), "standoff_BR": standoff(xR, yB),
}

# FLAT front assembly (kept for a print-ready STL: screen-face down, standoffs up)
front_flat = parts["front_panel"]
for n in ("standoff_FL", "standoff_FR", "standoff_BL", "standoff_BR"):
    front_flat = front_flat + parts[n]

# ---- stand the panel up at TILT (rotate about its bottom edge) ----
ROT = 180 - TILT
hinge = Axis((x_bot, 0, 0), (0, 1, 0))
for n in parts:
    parts[n] = parts[n].rotate(hinge, ROT)
mn = [1e9]*3; mx = [-1e9]*3
for shp in parts.values():
    b = shp.bounding_box()
    mn = [min(mn[i], v) for i, v in enumerate((b.min.X, b.min.Y, b.min.Z))]
    mx = [max(mx[i], v) for i, v in enumerate((b.max.X, b.max.Y, b.max.Z))]
shift = (-(mn[0]+mx[0])/2, -mn[1], -mn[2])
for n in parts:
    parts[n] = parts[n].move(Location(shift))
below = Box(4000, 4000, 800, align=(Align.CENTER, Align.CENTER, Align.MAX))
for n in parts:
    parts[n] = parts[n] - below

def fold(shp):
    return shp.rotate(hinge, ROT).move(Location(shift))
panel_min_x = mn[0] + shift[0]        # world X of the panel's bottom edge

# ---- base: flat slab behind the panel, front edge cut to the panel BACK face ----
BASE_LEN = 79.5
base = Box(BASE_LEN, PANEL_D, PANEL_T, align=(Align.MIN, Align.MIN, Align.MIN)).move(Location((panel_min_x, 0, 0)))
# remove base material in FRONT of the panel back face -> base butts flush to the panel
back_cut = fold(Box(3000, 3000, 3000, align=(Align.CENTER, Align.CENTER, Align.MAX)).move(Location((x_bot, cy, PANEL_T))))
base = base - back_cut
base = base - below
parts["base"] = base

# ---- 2 compact VERTICAL posts on the base, tops cut flush to the panel, M3 pilot ----
def foldpt(x, y, z):
    th = math.radians(ROT); c, s = math.cos(th), math.sin(th); px = x_bot
    xr = px + (x-px)*c + z*s
    zr = -(x-px)*s + z*c
    return (xr + shift[0], y + shift[1], zr + shift[2])

for i, by in enumerate(BOLT_YS):
    hx, hy, hz = foldpt(BOLT_X, by, PANEL_T)                 # panel back at the screw
    post = Cylinder(POST_OD/2, hz + 3, align=(Align.CENTER, Align.CENTER, Align.MIN)).move(Location((hx, hy, 0)))
    post = post - back_cut                                   # top face flush with the panel back
    pil  = fold(Cylinder((POST_PILOT+HOLE_COMP)/2, 40, align=(Align.CENTER, Align.CENTER, Align.MIN)).move(Location((BOLT_X, by, PANEL_T - 2))))
    parts[f"post_{['L','R'][i]}"] = (post - pil) - below

# ---- ENCLOSURE: close the base into a tub (sides + full back wall + roof) ----
# The front panel stays the removable lid; it seats on the wall front edges (60deg lean).
# Print the tub STANDING ON ITS BACK WALL so the roof/floor print as vertical walls.
WALL_T = 3.0
back_x  = panel_min_x + BASE_LEN            # base back edge, x
ym      = PANEL_D / 2                       # width center
_, _, H_TOP = foldpt(x_top, ym, PANEL_T)    # roof height = panel top (back face)
FB_X, _, _  = foldpt(x_bot, ym, PANEL_T)    # panel seat, front-bottom x
PT_X, _, _  = foldpt(x_top, ym, PANEL_T)    # panel seat, top x

# ---- trim the panel's top edge flush with the roof ----
# The top cut is straight across the panel THICKNESS (local z), so once tilted the
# screen-face corner (z=0) sits higher in world Z than the back-face corner (z=PANEL_T,
# which sets H_TOP) by PANEL_T*|cos(ROT)|. Slice that wedge off so the whole top edge
# lands level with the roof.
def unfold(shp):
    return shp.move(Location((-shift[0], -shift[1], -shift[2]))).rotate(hinge, -ROT)
top_trim = Box(4000, 4000, 800, align=(Align.CENTER, Align.CENTER, Align.MIN)).move(Location((0, 0, H_TOP)))
for n in ("front_panel", "standoff_FL", "standoff_FR", "standoff_BL", "standoff_BR"):
    parts[n] = parts[n] - top_trim
front_flat = front_flat - unfold(top_trim)

# side walls: wedge profile in X-Z, extruded WALL_T in Y, one per side
_side_prof = Plane.XZ * Polygon((FB_X, 0), (PT_X, H_TOP), (back_x, H_TOP), (back_x, 0), align=None)
_side = extrude(_side_prof, amount=WALL_T)
_b = _side.bounding_box()
parts["wall_L"] = _side.moved(Location((0, -_b.min.Y, 0))) - below       # Y=0 = screen-RIGHT
parts["wall_R"] = _side.moved(Location((0, PANEL_D - WALL_T - _b.min.Y, 0))) - below

# speaker grille in the RIGHT wall (wall_L, Y=0): slots over the folded cone-face patch
_spk_xb = x_bot - SPK_FROM_BOTTOM            # speaker bottom edge (local x)
_spk_xt = _spk_xb - SPK_H                    # speaker top edge (local x)
_spk_zc = PANEL_T + SPK_DEPTH/2              # cone-face depth center (local z)
_slot_len = SPK_DEPTH - 2*SPK_SLOT_INSET
_n = int(SPK_H // SPK_SLOT_PITCH)
_used = (_n - 1)*SPK_SLOT_PITCH
_start = (_spk_xb + _spk_xt)/2 + _used/2     # center the stack over the speaker height
for _i in range(_n):
    _sx = _start - _i*SPK_SLOT_PITCH
    _cut = fold(Box(SPK_SLOT_W, WALL_T + 4, _slot_len, align=(Align.CENTER, Align.CENTER, Align.CENTER)
                    ).move(Location((_sx, WALL_T/2, _spk_zc))))
    parts["wall_L"] = parts["wall_L"] - _cut

# speaker retention mount: bottom ledge + 2 corner snap clips, fused onto wall_L, holding
# the real speaker flush over the grille above (built in the panel-local frame, then folded
# into place exactly like the grille slots -- guaranteed to land on solid wall material).
_mnt_z0 = PANEL_T + SPK_MNT_PZ_SHIFT           # off the panel-seat seam at local z=PANEL_T
_mnt_z1 = _mnt_z0 + SPK_MNT_W
_mnt_y0 = WALL_T                                # wall's inner (interior-facing) face
# NOTE: Box(x_extent, y_extent, z_extent).move(Location((x, y, z))) in the panel-local frame,
# matching the grille-slot cut boxes above -- x=length(up/down slope), y=wall-normal, z=width.
_shelf = Box(SPK_LEDGE_T + 0.3, SPK_MNT_THK + SPK_MNT_CLR, _mnt_z1 - _mnt_z0,
             align=(Align.MIN, Align.MIN, Align.MIN)).move(Location((_spk_xb, _mnt_y0, _mnt_z0)))
_ledgelip = Box(SPK_LIP_H, SPK_LIP_REACH, _mnt_z1 - _mnt_z0, align=(Align.MIN, Align.MIN, Align.MIN)
               ).move(Location((_spk_xb - SPK_LIP_H, _mnt_y0 + SPK_MNT_THK + SPK_MNT_CLR - SPK_LIP_REACH, _mnt_z0)))
_mount = _shelf + _ledgelip

def _spk_top_clip(cz0, cz1):
    _post = Box(SPK_CLIP_POST, (SPK_MNT_THK + SPK_MNT_CLR) + 0.6, cz1 - cz0,
                align=(Align.MIN, Align.MIN, Align.MIN)
               ).move(Location((_spk_xt - SPK_CLIP_POST, _mnt_y0 - 0.3, cz0)))
    _tlip = Box(SPK_CLIP_POST + SPK_CLIP_REACH, SPK_CLIP_LIP_H, cz1 - cz0,
                align=(Align.MIN, Align.MIN, Align.MIN)
               ).move(Location((_spk_xt - SPK_CLIP_POST, _mnt_y0 + SPK_MNT_THK + SPK_MNT_CLR, cz0)))
    _tab = _post + _tlip
    _lead_x = _spk_xt + SPK_CLIP_REACH
    _lead = ShapeList([e for e in _tab.edges()
                        if abs(e.center().Y - (_mnt_y0 + SPK_MNT_THK + SPK_MNT_CLR)) < 1e-3
                        and abs(e.center().X - _lead_x) < 1e-3])
    return chamfer(_lead, SPK_CLIP_CHAM) if _lead else _tab

_mount = (_mount + _spk_top_clip(_mnt_z0 + SPK_CLIP_MARGIN, _mnt_z0 + SPK_CLIP_MARGIN + SPK_CLIP_W)
                 + _spk_top_clip(_mnt_z1 - SPK_CLIP_MARGIN - SPK_CLIP_W, _mnt_z1 - SPK_CLIP_MARGIN))
parts["wall_L"] = parts["wall_L"] + fold(_mount)

# full-height back wall -- plain, the USB-C mount lives on the LEFT wall instead (below).
back = Box(WALL_T, PANEL_D, H_TOP, align=(Align.MAX, Align.MIN, Align.MIN)).move(Location((back_x, 0, 0)))
parts["wall_back"] = back - below

# USB-C panel mount, on wall_R (screen-LEFT). Height stays at the original back-wall
# reference (near the floor, module rests on the base top face), just nudged up 1mm --
# NOT re-centered vertically on the wall. Horizontally: 10mm front of the wall's X
# center (toward the screen) -- still clear of the sloped front edge at this low height
# (edge sits at ~-20.7 there; the cutout+holes' footprint reaches only ~-5.3).
usbc_cz = PANEL_T + USBC_MOD_H/2 + 1.0
usbc_cx = (FB_X + back_x) / 2 - 10.0
_usbc_y = PANEL_D - WALL_T / 2            # wall_R's mid-thickness
parts["wall_R"] = parts["wall_R"] - Box(USBC_CUT_W, WALL_T + 2, USBC_CUT_H,
                                         align=(Align.CENTER, Align.CENTER, Align.CENTER)
                                        ).move(Location((usbc_cx, _usbc_y, usbc_cz)))
for dx in (-USBC_HOLE_DY, USBC_HOLE_DY):
    parts["wall_R"] = parts["wall_R"] - Cylinder((USBC_HOLE_D+HOLE_COMP)/2, WALL_T + 2, rotation=(90, 0, 0),
                                                  align=(Align.CENTER, Align.CENTER, Align.CENTER)
                                                 ).move(Location((usbc_cx + dx, _usbc_y, usbc_cz)))

# roof: slab from the panel top back to the back wall top
parts["roof"] = Box(back_x - PT_X, PANEL_D, WALL_T, align=(Align.MIN, Align.MIN, Align.MAX)
                    ).move(Location((PT_X, 0, H_TOP))) - below

# ---- top-corner bosses: the panel's 2 top screws thread into these (mirrors bottom posts) ----
# Built in the panel's local frame (against the back face at each top screw), then folded &
# fused to the side walls so the lid clamps at all 4 corners.
TOP_BOSS_HW  = 4.0     # boss half-width (local x) and reach toward the wall
TOP_BOSS_DEP = 9.0     # how far the boss stands off the panel back into the enclosure
for i, by in enumerate(BOLT_YS):
    y0, y1 = (0.0, by + TOP_BOSS_HW) if i == 0 else (by - TOP_BOSS_HW, PANEL_D)   # reach to the near wall
    boss = Box(2*TOP_BOSS_HW, y1 - y0, TOP_BOSS_DEP, align=(Align.CENTER, Align.MIN, Align.MIN)
               ).move(Location((TOP_BOLT_X, y0, PANEL_T)))
    boss = boss - Cylinder((POST_PILOT+HOLE_COMP)/2, TOP_BOSS_DEP + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)
                           ).move(Location((TOP_BOLT_X, by, PANEL_T - 1)))     # self-tap pilot
    parts[f"topboss_{['L','R'][i]}"] = fold(boss) - below

# ── Fuse into exactly TWO printable parts ─────────────────────────────────────
front_asm = parts["front_panel"]
for n in ("standoff_FL", "standoff_FR", "standoff_BL", "standoff_BR"):
    front_asm = front_asm + parts[n]                      # standoffs -> front panel
base_asm = (parts["base"] + parts["post_L"] + parts["post_R"]
            + parts["wall_L"] + parts["wall_R"] + parts["wall_back"] + parts["roof"]
            + parts["topboss_L"] + parts["topboss_R"])   # tub + top-corner bosses
out = {"front_panel": front_asm, "base": base_asm}

# ── Export ────────────────────────────────────────────────────────────────────
EXP = os.path.join(OUT, "exports")
os.makedirs(EXP, exist_ok=True)
def to_mesh(shape):
    t = os.path.join(EXP, "_t.stl"); export_stl(shape, t); m = trimesh.load(t); os.remove(t); return m
colors = {"front_panel":[150,150,150,255], "base":[170,120,210,255]}
scene = trimesh.Scene()
for n, shp in out.items():
    m = to_mesh(shp); m.visual.face_colors = colors[n]
    scene.add_geometry(m, node_name=n, geom_name=n)
scene.export(os.path.join(EXP, "case.3mf"))
scene.export(os.path.join(EXP, "case.glb"))

# ---- separate print-ready STL per part (each printed separately) ----
export_stl(front_flat, os.path.join(EXP, "front_panel.stl"))   # flat: screen-face down
export_stl(base_asm,   os.path.join(EXP, "base.stl"))          # tub; print STANDING ON BACK WALL
print("parts:", ", ".join(out))
print("STL: front_panel.stl (flat) + base.stl (printed separately)")
print(f"2 M3 screws at bottom corners y={BOLT_YS}, x={BOLT_X}")
print("Saved case.3mf + case.glb")
