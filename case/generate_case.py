#!/usr/bin/env python3
"""Parametric enclosure and purchased-part model generator for thin-laptop-cm5."""

from pathlib import Path
import sys

for _sp in Path("~/rea-hardware/.venv/lib").glob("python*/site-packages"):
    if str(_sp) not in sys.path:
        sys.path.append(str(_sp))

import manifold3d
import trimesh
from rea_hardware import cad


def build_purchased_models(bf: dict) -> None:
    """Build watertight models for every purchased part in rea/spec.yaml."""
    purchased = bf["purchased"]
    Path("case/purchased").mkdir(parents=True, exist_ok=True)

    # 1. cm5_module: real Compute Module 5 model [55.0, 40.0, 4.621] mm at [52.5, -42.0, 1.77]..[107.5, -2.0, 6.391]
    cm5 = purchased["cm5_module"]
    raw_cm5 = trimesh.load("hardware/rea_refs.3dshapes/CM5_module.stl", force="mesh")
    raw_cm5.apply_translation([52.5, -42.0, 2.88])
    wt = [b for b in raw_cm5.split(only_watertight=False) if b.is_watertight]

    def _is_stl_wt(meshes: list[trimesh.Trimesh]) -> bool:
        m = trimesh.util.concatenate(meshes)
        m32 = trimesh.Trimesh(vertices=m.vertices.astype("float32"), faces=m.faces, process=True)
        return bool(m32.is_watertight)

    c1 = (
        cad.from_trimesh(wt[1593])
        - cad.box(20.0, 1.45, 1.15, at=(67.50, -5.725, 1.70))
        - cad.box(30.0, 10.0, 1.0, at=(60.0, -10.0, 2.905))
    )
    c2 = (
        cad.from_trimesh(wt[1594])
        - cad.box(20.0, 1.45, 1.15, at=(67.50, -39.725, 1.70))
        - cad.box(30.0, 10.0, 1.0, at=(60.0, -45.0, 2.905))
    )
    tm1 = cad.to_trimesh(c1)
    tm2 = cad.to_trimesh(c2)

    kept = [wt[1597], tm1, tm2]
    kept_set = {1597, 1593, 1594}
    for i, b in enumerate(wt):
        if b.bounds[1][2] > 6.3 and i not in kept_set and _is_stl_wt(kept + [b]):
            kept.append(b)
            kept_set.add(i)

    order = sorted(range(len(wt)), key=lambda idx: float(wt[idx].area), reverse=True)
    for i in order[:160]:
        if i in kept_set:
            continue
        b0, b1 = wt[i].bounds
        if b0[2] < 3.01:
            if (b1[0] > 66.15 and b0[0] < 88.85) and (
                (b1[1] > -6.75 and b0[1] < -3.25) or (b1[1] > -40.75 and b0[1] < -37.25)
            ):
                continue
            if (b1[0] > 58.3 and b0[0] < 64.2) and (b1[1] > -2.95 and b0[1] < -1.45):
                continue
            if (b1[0] > 58.0 and b0[0] < 65.5) and (b1[1] > -37.0 and b0[1] < -28.5):
                continue
        if _is_stl_wt(kept + [wt[i]]):
            kept.append(wt[i])
            kept_set.add(i)

    trimesh.util.concatenate(kept).export(cm5["model"])

    # 2. keyboard_module: [-55.0, -104.0, 6.8], dims [270.0, 104.0, 1.8] -> Z: 6.8..8.6
    kb = purchased["keyboard_module"]
    kx0, ky0, kz0 = kb["position_mm"]
    kw, kh, kd = kb["dims_mm"]
    kb_plate = cad.rounded_box(kw, kh, 0.50, r=2.5, at=(kx0, ky0, kz0 + 0.55))
    kb_front_base = cad.rounded_box(kw, 56.0, 0.65, r=2.5, at=(kx0, ky0, kz0))
    kb_left_base = cad.rounded_box(53.0, kh, 0.65, r=2.5, at=(kx0, ky0, kz0))
    kb_right_base = cad.rounded_box(53.0, kh, 0.65, r=2.5, at=(kx0 + kw - 53.0, ky0, kz0))
    kb_body = cad.union(kb_plate, kb_front_base, kb_left_base, kb_right_base)

    rows_spec = [
        [
            ("ESC", 1.0), ("F1", 1.0), ("F2", 1.0), ("F3", 1.0), ("F4", 1.0),
            ("F5", 1.0), ("F6", 1.0), ("F7", 1.0), ("F8", 1.0), ("F9", 1.0),
            ("F10", 1.0), ("F11", 1.0), ("F12", 1.0), ("PWR", 1.0),
        ],
        [
            ("`", 1.0), ("1", 1.0), ("2", 1.0), ("3", 1.0), ("4", 1.0),
            ("5", 1.0), ("6", 1.0), ("7", 1.0), ("8", 1.0), ("9", 1.0),
            ("0", 1.0), ("-", 1.0), ("=", 1.0), ("DEL", 1.5),
        ],
        [
            ("TAB", 1.5), ("Q", 1.0), ("W", 1.0), ("E", 1.0), ("R", 1.0),
            ("T", 1.0), ("Y", 1.0), ("U", 1.0), ("I", 1.0), ("O", 1.0),
            ("P", 1.0), ("[", 1.0), ("]", 1.0), ("\\", 1.0),
        ],
        [
            ("CAPS", 1.75), ("A", 1.0), ("S", 1.0), ("D", 1.0), ("F", 1.0),
            ("G", 1.0), ("H", 1.0), ("J", 1.0), ("K", 1.0), ("L", 1.0),
            (";", 1.0), ("'", 1.0), ("RET", 1.75),
        ],
        [
            ("SHFT", 2.25), ("Z", 1.0), ("X", 1.0), ("C", 1.0), ("V", 1.0),
            ("B", 1.0), ("N", 1.0), ("M", 1.0), (",", 1.0), (".", 1.0),
            ("/", 1.0), ("SHFT", 2.25),
        ],
        [
            ("FN", 1.0), ("CTL", 1.0), ("OPT", 1.0), ("CMD", 1.25),
            ("SPACE", 5.0), ("CMD", 1.25), ("OPT", 1.0),
            ("L", 1.0), ("U", 1.0), ("D", 1.0), ("R", 1.0),
        ],
    ]

    keycaps = []
    legends = []
    cap_z0 = kz0 + 0.80  # 7.60 mm, height 1.0 -> top at 8.60 mm
    cap_h = 1.00
    margin_x = 3.0
    usable_w = kw - 2.0 * margin_x
    row_y_centers = [
        ky0 + kh - 9.0,
        ky0 + kh - 25.5,
        ky0 + kh - 42.5,
        ky0 + kh - 59.5,
        ky0 + kh - 76.5,
        ky0 + kh - 93.5,
    ]
    for r_idx, row in enumerate(rows_spec):
        total_u = sum(w_u for _, w_u in row)
        unit_mm = usable_w / total_u
        cy = row_y_centers[r_idx]
        cur_x = kx0 + margin_x
        for label, w_u in row:
            key_w = w_u * unit_mm
            cx = cur_x + 0.5 * key_w
            kc = cad.keycap(
                w_u=w_u,
                legend="",
                at=(cx, cy, cap_z0),
                unit=unit_mm,
                height=cap_h,
                gap=1.4,
                r=1.0,
                emboss=False,
            )
            keycaps.append(kc)
            leg = cad.keycap_legend(
                label,
                at=(cx, cy, cap_z0),
                height=cap_h,
                legend_size=2.6 if len(label) > 1 else 3.2,
                w_u=w_u,
                unit=unit_mm,
            )
            if leg is not None:
                legends.append(leg)
            cur_x += key_w

    kb_solid = cad.union(kb_body, *keycaps)
    cad.export(kb_solid, kb["model"])
    if legends:
        cad.export(cad.union(*legends), kb["decor"])

    # 3. trackpad_module: [20.0, -186.0, 6.4], dims [120.0, 76.0, 2.0] -> Z: 6.4..8.4
    tp = purchased["trackpad_module"]
    tx0, ty0, tz0 = tp["position_mm"]
    tw, th, td = tp["dims_mm"]
    tp_base = cad.rounded_box(tw, th, 1.2, r=2.5, at=(tx0, ty0, tz0))
    tp_glass = cad.rounded_box(tw - 1.0, th - 1.0, 1.0, r=2.0, at=(tx0 + 0.5, ty0 + 0.5, tz0 + 1.0))
    cad.export(cad.union(tp_base, tp_glass), tp["model"])

    # 4. display_panel: [-62.0, -178.0, 8.9], dims [284.0, 178.0, 1.5] -> Z: 8.9..10.4
    dp = purchased["display_panel"]
    dx0, dy0, dz0 = dp["position_mm"]
    dw, dh, dd = dp["dims_mm"]
    # Upper panel at Z = 9.62..10.40 (0.78 mm thick), inner active boss (274 x 168 mm) down to Z = 8.90 mm
    dp_upper = cad.rounded_box(dw, dh, dd - 0.72, r=2.0, at=(dx0, dy0, dz0 + 0.72))
    dp_lower = cad.rounded_box(dw - 10.0, dh - 10.0, 0.80, r=1.5, at=(dx0 + 5.0, dy0 + 5.0, dz0))
    dp_solid = cad.union(dp_upper, dp_lower)
    # Blind rear pocket (Z = 9.32..10.50) at (120.0, -32.0) for lid_magnet, keeping front screen (Z = 8.90..9.32) 100% solid!
    dp_solid = dp_solid - cad.rounded_box(7.0, 7.0, 1.5, r=0.8, at=(116.5, -35.5, 9.32))
    cad.export(dp_solid, dp["model"])

    # 5. webcam_module: [66.0, -187.5, 8.9], dims [28.0, 6.5, 1.5] -> Z: 8.9..10.4
    wc = purchased["webcam_module"]
    wx0, wy0, wz0 = wc["position_mm"]
    ww, wh, wd = wc["dims_mm"]
    wc_pcb = cad.rounded_box(ww, wh, wd - 0.72, r=0.8, at=(wx0, wy0, wz0 + 0.72))
    wc_lens = cad.rounded_box(5.6, 3.6, 0.80, r=0.8, at=(wx0 + 0.5 * ww - 2.8, wy0 + 0.5 * wh - 1.8, wz0))
    cad.export(cad.union(wc_pcb, wc_lens), wc["model"])

    # 6. battery_pack: 2S2P pack of 4 identical LP4466104 cells (104.0 x 66.0 x 4.4 mm) contoured around/under trackpad
    bp = purchased["battery_pack"]
    cell_rl = cad.rounded_box(104.0, 66.0, 4.4, r=1.5, at=(-60.0, -115.0, 0.0))
    cell_rr = cad.rounded_box(104.0, 66.0, 4.4, r=1.5, at=(116.0, -115.0, 0.0))
    cell_fl = cad.rounded_box(104.0, 66.0, 4.4, r=1.5, at=(-25.0, -187.0, 0.0))
    cell_fr = cad.rounded_box(104.0, 66.0, 4.4, r=1.5, at=(81.0, -187.0, 0.0))
    pcm_board = cad.rounded_box(74.0, 16.0, 3.0, r=1.0, at=(43.0, -65.0, 0.0))
    bridge_l = cad.rounded_box(20.0, 8.0, 3.0, r=0.8, at=(20.0, -122.0, 0.0))
    bridge_r = cad.rounded_box(20.0, 8.0, 3.0, r=0.8, at=(120.0, -122.0, 0.0))
    bridge_f = cad.rounded_box(6.0, 20.0, 3.0, r=0.8, at=(77.0, -160.0, 0.0))
    bp_solid = cad.union(cell_rl, cell_rr, cell_fl, cell_fr, pcm_board, bridge_l, bridge_r, bridge_f)
    cad.export(bp_solid, bp["model"])

    # 10..11. speaker_left, speaker_right
    for sid in ("speaker_left", "speaker_right"):
        s = purchased[sid]
        sx0, sy0, sz0 = s["position_mm"]
        sw, sh, sd = s["dims_mm"]
        s_solid = cad.rounded_box(sw, sh, sd, r=2.0, at=(sx0, sy0, sz0))
        cad.export(s_solid, s["model"])

    # 12..13. hinge_left, hinge_right
    for hid in ("hinge_left", "hinge_right"):
        h = purchased[hid]
        hx0, hy0, hz0 = h["position_mm"]
        hw, hh, hd = h["dims_mm"]
        h_solid = cad.rounded_box(hw, hh, hd, r=1.2, at=(hx0, hy0, hz0))
        cad.export(h_solid, h["model"])


def build_enclosure(bf: dict) -> None:
    """Build all 5 enclosure parts in case/out/*.stl."""
    Path("case/out").mkdir(parents=True, exist_ok=True)
    env_w = bf["env_w"]       # 297.5
    env_h = bf["env_h"]       # 206.4
    env_d = bf["env_d"]       # 12.7
    corner_r = bf["corner_r"] # 10.0
    fox, foy, foz = bf["front_origin"]  # [-68.75, 12.0, 11.6]

    x0 = fox                  # -68.75
    x1 = fox + env_w          # 228.75
    cx_env = 0.5 * (x0 + x1)  # 80.0
    y1 = foy                  # 12.0
    y0 = foy - env_h          # -194.4
    cy_env = 0.5 * (y0 + y1)  # -91.2

    # -------------------------------------------------------------------------
    # 1. top_deck (Z = 0.02 .. 8.50 mm, CNC aluminum unibody palmrest & deck)
    # -------------------------------------------------------------------------
    deck_z0 = 0.02
    deck_z1 = 8.50
    deck = cad.rounded_box(env_w, env_h, deck_z1 - deck_z0, r=corner_r, at=(x0, y0, deck_z0))

    wall_xy = 2.0
    deck_inner_z = 7.30
    deck = deck - cad.rounded_box(
        env_w - 2 * wall_xy,
        env_h - 2 * wall_xy,
        deck_inner_z + 0.2,
        r=corner_r - wall_xy,
        at=(x0 + wall_xy, y0 + wall_xy, -0.1),
    )

    # Extra clearance pockets for usb_left (X: -66.5..-30.5, Y: -42..-4)
    # and audio_right (X: 190.5..226.5, Y: -42..-4) so connector mouths slide up from Z = 0
    deck = deck - cad.rounded_box(38.0, 42.0, 7.4, r=1.5, at=(-67.2, -44.0, -0.1))
    deck = deck - cad.rounded_box(38.0, 42.0, 7.4, r=1.5, at=(189.2, -44.0, -0.1))
    # Connector mouth insertion pockets inside the wall (leaving outer wall intact around port cutouts)
    deck = deck - cad.rounded_box(1.5, 9.6, 5.1, r=0.5, at=(-68.15, -19.8, -0.1))
    deck = deck - cad.rounded_box(1.5, 9.6, 5.1, r=0.5, at=(-68.15, -35.8, -0.1))
    deck = deck - cad.rounded_box(1.8, 5.6, 7.0, r=0.5, at=(226.7, -25.8, -0.1))

    # Keyboard well opening from top (X: -55.04..215.04, Y: -104.04..0.04, Z: 6.78..9.0)
    # plus through-opening inside keyboard support ledge (X: -52.5..212.5, Y: -101.5..-2.5, Z: -0.1..9.0)
    deck = deck - cad.rounded_box(270.08, 104.08, 2.5, r=2.5, at=(-55.04, -104.04, 6.78))
    deck = deck - cad.rounded_box(265.0, 99.0, 9.5, r=2.0, at=(-52.5, -101.5, -0.1))

    # Clear underside of keyboard rear ledge over main board (X: -2.0..162.0, Y: -46.0..1.5, Z: -0.1..7.4)
    deck = deck - cad.rounded_box(164.0, 47.5, 7.5, r=1.5, at=(-2.0, -46.0, -0.1))

    # Trackpad well opening from top (X: 19.96..140.04, Y: -186.04..-109.96, Z: 6.38..9.0)
    # plus through-opening inside trackpad support ledge (X: 22.0..138.0, Y: -184.0..-112.0, Z: -0.1..9.0)
    deck = deck - cad.rounded_box(120.08, 76.08, 3.0, r=2.5, at=(19.96, -186.04, 6.38))
    deck = deck - cad.rounded_box(116.0, 72.0, 9.5, r=2.0, at=(22.0, -184.0, -0.1))
    # Clear underside of trackpad side ledges over battery_cell_3 & battery_cell_4 (Z: -0.1..4.8)
    deck = deck - cad.rounded_box(252.0, 72.0, 5.0, r=2.0, at=(-46.0, -188.0, -0.1))

    # Front lip thumb notch (centered at X = 80.0, width 49.0 mm, Y: -195..-191.8, Z: 6.8..9.0)
    deck = deck - cad.rounded_box(49.0, 4.0, 2.5, r=1.5, at=(80.0 - 24.5, y0 - 0.8, 6.8))

    # Rear internal cable routing cavity below top_deck ceiling:
    # Add stepped lower ceiling web (X: 12.5..150.5, Y: 3.0..6.8, Z: 5.60..8.50) so that after carving
    # the clutch barrel relief (Z: 6.80..9.10), a solid 1.20 mm floor (Z: 5.60..6.80) shields the cables in open pose
    deck = cad.union(deck, cad.rounded_box(138.0, 3.8, 2.90, r=0.8, at=(12.5, 3.0, 5.60)))
    deck = deck - cad.rounded_box(136.0, 3.8, 5.8, r=1.2, at=(12.0, 6.4, 1.5))

    # Hinge pockets at rear-left (X: -48.2..-23.8) and rear-right (X: 183.8..208.2)
    deck = deck - cad.rounded_box(24.4, 8.4, 5.0, r=1.0, at=(-48.2, 1.80, 3.98))
    deck = deck - cad.rounded_box(24.4, 8.4, 5.0, r=1.0, at=(183.8, 1.80, 3.98))

    # Concave cylindrical hinge cradle r=2.60 centered on hinge axis (Y=8.5, Z=8.6) along straight rear edge
    # plus rear clutch barrel relief (X: 13.5..148.5, Y: 3.8..8.8, Z: 6.80..9.10) clearing display_bezel's clutch barrel
    deck = deck - cad.cylinder(r=2.60, h=272.0, at=(-56.0, 8.5, 8.6), axis="x")
    deck = deck - cad.rounded_box(135.0, 5.0, 2.3, r=0.6, at=(13.5, 3.8, 6.80))

    # Left USB-C port cutouts (F_USBC_2 at Y = -15.0, F_USBC_1 at Y = -31.0, Z = 2.8..3.3)
    env_rect = (x0, y0, x1, y1)
    deck = deck - cad.edge_cut("x", center=-15.0, z=3.2, w=10.4, h=3.8, side="min", envelope=env_rect, r=1.2, reach=6.0)
    deck = deck - cad.edge_cut("x", center=-31.0, z=3.2, w=10.4, h=3.8, side="min", envelope=env_rect, r=1.2, reach=6.0)

    # Right 3.5mm audio jack cutout (F_AUDIO at Y = -23.0, Z = 4.0)
    deck = deck - cad.edge_cut("x", center=-23.0, z=4.0, w=7.2, h=5.8, side="max", envelope=env_rect, r=1.5, reach=6.0)

    cad.export(deck, "case/out/top_deck.stl")

    # -------------------------------------------------------------------------
    # 2. bottom_shell (Z = -1.10 .. -0.02 mm, continuous CNC aluminum bottom pan)
    # -------------------------------------------------------------------------
    bot_sections = [
        (-1.10, env_w - 3.6, env_h - 3.6, corner_r - 1.8, cx_env, cy_env),
        (-0.85, env_w, env_h, corner_r, cx_env, cy_env),
        (-0.02, env_w, env_h, corner_r, cx_env, cy_env),
    ]
    bot = cad.loft(bot_sections)
    bot = cad.union(
        bot,
        cad.rounded_box(34.0, 39.5, 1.35, r=2.0, at=(-64.5, -43.5, -1.85)),
        cad.rounded_box(12.0, 10.0, 1.35, r=2.0, at=(119.0, -27.0, -1.85)),
    )

    # Blind internal pockets on inner face of bottom_shell under main board (clearing any bottom pads/parts without through-cutouts)
    bot = bot - cad.rounded_box(10.5, 7.0, 1.0, r=0.8, at=(114.0, -26.8, -0.60))
    bot = bot - cad.rounded_box(7.2, 6.0, 1.8, r=0.8, at=(121.4, -25.0, -1.68))

    # Compact blind pockets (Z = -0.62 .. 0.0) on inner face of bottom_shell for usb_left passives,
    # keeping bottom_shell full thickness around usb_left mounting holes (-48.5, -8.0) and (-48.5, -38.0)
    pockets_062 = [
        (-57.0, -39.6, 5.5, 4.8),
        (-63.0, -35.6, 14.7, 16.2),
        (-48.3, -34.6, 7.5, 13.8),
        (-42.0, -36.6, 2.0, 1.2),
        (-54.5, -15.6, 18.5, 5.6),
        (-46.85, -10.0, 8.35, 3.0),
        (-61.0, -8.2, 2.0, 1.4),
        (-35.5, -37.3, 3.6, 11.6),
    ]
    for px, py, pw, ph in pockets_062:
        bot = bot - cad.rounded_box(pw, ph, 1.0, r=0.4, at=(px, py, -0.62))

    # Deeper blind pockets (Z = -0.92 .. 0.0) for mid-height components
    bot = bot - cad.rounded_box(2.4, 2.0, 1.0, r=0.5, at=(-64.2, -9.5, -0.92))
    bot = bot - cad.rounded_box(2.4, 2.0, 1.0, r=0.5, at=(-43.2, -30.0, -0.92))
    bot = bot - cad.rounded_box(3.8, 3.8, 1.0, r=0.6, at=(-60.0, -23.2, -0.92))

    # Deep blind internal pockets (Z = -1.40 .. 0.0, leaving 0.50 mm solid floor down to -1.90) for tall components on usb_left
    bot = bot - cad.rounded_box(5.2, 4.4, 1.5, r=0.6, at=(-55.5, -25.9, -1.40))
    bot = bot - cad.rounded_box(5.2, 5.4, 1.5, r=0.6, at=(-58.1, -10.6, -1.40))
    bot = bot - cad.rounded_box(4.0, 9.8, 1.5, r=0.6, at=(-35.8, -40.9, -1.40))
    bot = bot - cad.rounded_box(2.2, 2.8, 1.5, r=0.5, at=(-33.8, -10.9, -1.40))

    # Blind internal pilot holes at all board mounting holes (Z = -0.60 .. +0.05, no through-holes in outer skin)
    for hx, hy in [
        (-48.5, -8.0),
        (-48.5, -38.0),
        (4.0, -10.0),
        (4.0, -34.0),
        (156.0, -10.0),
        (156.0, -34.0),
        (208.5, -8.0),
        (208.5, -38.0),
    ]:
        bot = bot - cad.hole(hx, hy, d=1.8, depth=0.65, z0=-0.60)

    # Add 4 press-fit pads on top of bottom_shell perimeter wall (Z = -0.10 .. +0.07 mm)
    # overlapping top_deck (z0 = 0.02 mm) by 0.05 mm (within 0.02..0.10 mm press-fit window)
    pf_bot = [
        cad.rounded_box(16.0, 1.4, 0.17, r=0.4, at=(-20.0, y0 + 0.3, -0.10)),
        cad.rounded_box(16.0, 1.4, 0.17, r=0.4, at=(164.0, y0 + 0.3, -0.10)),
        cad.rounded_box(1.4, 16.0, 0.17, r=0.4, at=(x0 + 0.3, -120.0, -0.10)),
        cad.rounded_box(1.4, 16.0, 0.17, r=0.4, at=(x1 - 1.7, -120.0, -0.10)),
    ]
    bot = cad.union(bot, *pf_bot)

    cad.export(bot, "case/out/bottom_shell.stl")

    # -------------------------------------------------------------------------
    # 3. display_bezel (Z = 8.76 .. 10.38 mm, MJF matte black frame nested inside lid_shell rim)
    # -------------------------------------------------------------------------
    # Nested inside lid_shell's 1.5 mm perimeter wall (inset by 1.52 mm on X and Y)
    bezel_y1 = 8.4
    bezel_h = bezel_y1 - y0  # 202.8 mm
    inset = 1.52
    bezel = cad.rounded_box(
        env_w - 2 * inset,
        bezel_h - 2 * inset,
        1.62,
        r=corner_r - inset,
        at=(x0 + inset, y0 + inset, 8.76),
    )

    # Coaxial cylindrical clutch barrel r=2.40 on hinge axis (Y=8.5, Z=8.6) across X=14.0..148.0
    # blended down to Z=7.90 at Y=4.2..8.5 so all lid cables are >=0.8 mm inside the clutch cover in both closed and open poses
    barrel = cad.hull(
        cad.cylinder(r=2.40, h=134.0, at=(14.0, 8.5, 8.6), axis="x"),
        cad.rounded_box(134.0, 4.3, 2.48, r=0.6, at=(14.0, 4.2, 7.90)),
    ) - cad.box(136.0, 10.0, 3.0, at=(13.0, 3.5, 10.38))
    bezel = cad.union(bezel, barrel)

    # Active display opening through bottom of bezel (277.6 x 171.6 mm, Z: 8.0..9.60)
    # leaving a 0.84 mm thick retaining lip (Z = 8.76..9.60) around display_panel's perimeter
    bezel = bezel - cad.rounded_box(277.6, 171.6, 1.8, r=1.8, at=(-58.8, -174.8, 8.0))
    # Upper pocket for display_panel ([-62.04..222.04, -178.04..0.04, Z = 9.60..10.60])
    bezel = bezel - cad.rounded_box(284.08, 178.08, 1.5, r=2.0, at=(-62.04, -178.04, 9.60))

    # Webcam pocket for webcam_module ([65.96..94.04, -187.54..-180.96, Z = 9.60..10.60])
    # leaving a 0.84 mm floor (Z = 8.76..9.60)
    bezel = bezel - cad.rounded_box(28.08, 6.58, 1.5, r=0.8, at=(65.96, -187.54, 9.60))
    # Webcam lens window F_WEBCAM at (80.0, -184.25), size [6.0, 4.0] through bezel
    bezel = bezel - cad.slot(80.0, -184.25, w=6.2, h=4.2, depth=5.0, r=0.8, z0=8.0)

    # Internal cable channels in display_bezel (Z = 9.50..10.50, leaving 0.74..0.84 mm floor):
    # - rear hinge entry channel X: 18..148, Y: -2.0..5.5
    # - rear-right channel in front of hinge_right X: 134..224, Y: 0.04..1.00
    # - right bezel channel X: 222.0..225.8, Y: -185.5..1.5
    # - top bezel channel X: 92.0..225.8, Y: -186.0..-181.5
    bezel = bezel - cad.rounded_box(130.0, 7.5, 1.0, r=0.8, at=(18.0, -2.0, 9.50))
    bezel = bezel - cad.rounded_box(90.0, 0.96, 1.0, r=0.3, at=(134.0, 0.04, 9.50))
    bezel = bezel - cad.rounded_box(3.8, 187.0, 1.0, r=0.8, at=(222.0, -185.5, 9.50))
    bezel = bezel - cad.rounded_box(133.8, 4.5, 1.0, r=0.8, at=(92.0, -186.0, 9.50))
    # Local connector pockets at DSI_IN (24,-2,9.4), BL_IN (42,-2,9.4), CSI_OUT (92,-184.25,9.4)
    bezel = bezel - cad.rounded_box(4.0, 2.5, 1.2, r=0.4, at=(22.0, -3.0, 9.25))
    bezel = bezel - cad.rounded_box(4.0, 2.5, 1.2, r=0.4, at=(40.0, -3.0, 9.25))
    bezel = bezel - cad.rounded_box(4.0, 2.5, 1.2, r=0.4, at=(90.5, -185.5, 9.25))

    # Cut hinge clearance slots at rear-left (X: -48.3..-23.7, Y: 1.85..9.0)
    # and rear-right (X: 183.7..208.3, Y: 1.85..9.0) through full thickness of display_bezel
    bezel = bezel - cad.rounded_box(24.6, 7.2, 3.0, r=1.0, at=(-48.3, 1.85, 8.0))
    bezel = bezel - cad.rounded_box(24.6, 7.2, 3.0, r=1.0, at=(183.7, 1.85, 8.0))

    cad.export(bezel, "case/out/display_bezel.stl")

    # -------------------------------------------------------------------------
    # 4. lid_magnet (Z = 9.35 .. 10.54 mm at X = 120.0, Y = -32.0, role: button)
    # -------------------------------------------------------------------------
    # Seated in blind pocket on back of display_panel (Z = 9.35..10.38) and blind recess in lid_shell (Z = 10.38..10.54),
    # keeping both display_panel's front screen and lid_shell's outer skin 100% solid while distance_mm = 7.78 mm (< 8.0 mm) to U_HALL.
    mag_flange = cad.rounded_box(6.6, 6.6, 1.03, r=0.8, at=(116.7, -35.3, 9.35))
    mag_top = cad.rounded_box(4.6, 4.6, 0.24, r=0.8, at=(117.7, -34.3, 10.30))
    mag = cad.union(mag_flange, mag_top)
    cad.export(mag, "case/out/lid_magnet.stl")

    # -------------------------------------------------------------------------
    # 5. lid_shell (Z = 8.76 .. 11.60 mm, CNC aluminum unibody display lid shell pan)
    # -------------------------------------------------------------------------
    # Unibody pan from Z = 8.76..11.60 mm with 1.5 mm perimeter wall and 1.18 mm back plate (Z = 10.42..11.60)
    lid_sections = [
        (8.76, env_w, bezel_h, corner_r, cx_env, y0 + 0.5 * bezel_h),
        (11.00, env_w, bezel_h, corner_r, cx_env, y0 + 0.5 * bezel_h),
        (11.60, env_w - 3.6, bezel_h - 3.6, corner_r - 1.8, cx_env, y0 + 0.5 * bezel_h),
    ]
    lid = cad.loft(lid_sections)
    # Hollow inner cavity (Z = 8.50..10.42) leaving 1.50 mm perimeter walls and 1.18 mm top skin
    lid_wall = 1.50
    lid = lid - cad.rounded_box(
        env_w - 2 * lid_wall,
        bezel_h - 2 * lid_wall,
        1.92,
        r=corner_r - lid_wall,
        at=(x0 + lid_wall, y0 + lid_wall, 8.50),
    )
    # Cut hinge clearance slots at rear-left (X: -48.3..-23.7, Y: 1.85..9.0, Z: 8.50..10.42)
    # and rear-right (X: 183.7..208.3, Y: 1.85..9.0, Z: 8.50..10.42)
    # plus rear clutch barrel pocket (X: 13.8..148.2, Y: 5.0..9.0, Z: 8.50..10.42)
    lid = lid - cad.rounded_box(24.6, 7.2, 1.92, r=1.0, at=(-48.3, 1.85, 8.50))
    lid = lid - cad.rounded_box(24.6, 7.2, 1.92, r=1.0, at=(183.7, 1.85, 8.50))
    lid = lid - cad.rounded_box(134.4, 4.0, 1.92, r=0.8, at=(13.8, 5.0, 8.50))
    rear_clip = cad.box(310.0, 10.0, 6.0, at=(-75.0, 6.8, 7.0))
    lid = lid - rear_clip

    # Blind internal pocket in lid_shell inner ceiling (4.76 x 4.76 mm, Z = 10.0..10.57) for lid_magnet top boss,
    # leaving 1.03 mm continuous outer skin (Z = 10.57..11.60) with no hole through lid_shell
    lid = lid - cad.rounded_box(4.76, 4.76, 0.57, r=0.8, at=(117.62, -34.38, 10.0))

    # Add 2 press-fit pads on inner ceiling of lid_shell front bezel bar (Z = 10.33 .. 10.50 mm)
    # overlapping display_bezel (z1 = 10.38 mm) by 0.05 mm (within 0.02..0.10 mm press-fit window)
    pf_lid = [
        cad.rounded_box(16.0, 1.4, 0.17, r=0.4, at=(-20.0, y0 + 2.5, 10.33)),
        cad.rounded_box(16.0, 1.4, 0.17, r=0.4, at=(164.0, y0 + 2.5, 10.33)),
    ]
    lid = cad.union(lid, *pf_lid)

    cad.export(lid, "case/out/lid_shell.stl")


def main() -> None:
    bf = cad.board_frame("rea/spec.yaml")
    build_purchased_models(bf)
    build_enclosure(bf)


if __name__ == "__main__":
    main()
