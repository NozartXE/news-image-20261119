"""Parametric scene painters for the news-image engine.

Every painter takes (draw, box, spec) and draws ONE story as a scene:
an actor, a setting and an action, composed horizontally so it stays
identifiable in a wide, short letterbox at 480 px contact scale.
Bold flat shapes and silhouettes; no photographic detail. All
coordinates are fractions of the box, so a painter works at hero
size and at card size. Deterministic: pseudo-random scatter uses a
fixed-seed LCG defined here, never the global random state.
"""

import math

from .textutil import SANS_BOLD, centred, font, gradient, lerp, text_w

INK = (24, 22, 20)
PAPER = (247, 242, 231)
ACCENT = (156, 38, 24)
NAVY = (18, 38, 66)
GOLD = (198, 148, 42)
WHITE = (250, 248, 242)


class LCG:
    """Fixed-seed linear congruential generator (deterministic)."""

    def __init__(self, seed):
        self.s = seed % 2147483648

    def next(self, lo, hi):
        self.s = (1103515245 * self.s + 12345) % 2147483648
        return lo + (self.s % 100000) / 100000.0 * (hi - lo)


def _label(draw, cx, y, s, size, fill, bg=None, box=None):
    """Centred in-scene label; when box is given, clamped inside it."""
    fnt = font(SANS_BOLD, size)
    w = text_w(draw, s, fnt)
    if box is not None:
        x0, y0, x1, y1 = box
        cx = min(max(cx, x0 + w / 2 + 5), x1 - w / 2 - 5)
        y = min(max(y, y0 + 2), y1 - size - 5)
    if bg is not None:
        draw.rectangle([cx - w / 2 - 4, y - 2, cx + w / 2 + 4, y + size + 3],
                       fill=bg)
    draw.text((cx - w / 2, y), s, font=fnt, fill=fill)


def _star5(draw, cx, cy, r, fill):
    """A five-pointed star polygon — a dot does not read as a star."""
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    draw.polygon(pts, fill=fill)


# ------------------------------------------------------------------ sea
def sea_strike(draw, box, spec):
    """Dusk sea: a tanker, an island headland, one strike burst."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    sea_y = y0 + int(h * 0.58)
    sky_top, sky_mid, sky_low = (43, 32, 66), (148, 62, 44), (232, 138, 62)
    for yy in range(y0, sea_y):
        t = (yy - y0) / max(1, sea_y - y0)
        col = lerp(sky_top, sky_mid, t / 0.55) if t < 0.55 else \
            lerp(sky_mid, sky_low, (t - 0.55) / 0.45)
        draw.line([(x0, yy), (x1, yy)], fill=col)
    # one sun only: a small half-disc on the horizon, far left
    sr = max(6, int(h * 0.09))
    scx, scy = x0 + int(w * 0.10), sea_y
    draw.pieslice([scx - sr, scy - sr, scx + sr, scy + sr], start=180, end=360,
                  fill=(246, 196, 96))
    # sea
    draw.rectangle([x0, sea_y, x1, y1], fill=(26, 44, 66))
    rng = LCG(41)
    for yy in range(sea_y + 6, y1 - 4, max(6, int(h * 0.09))):
        xx = x0 + 8
        while xx < x1 - 40:
            ln = rng.next(18, 44)
            draw.line([(xx, yy), (xx + ln, yy)], fill=(74, 104, 132), width=2)
            xx += ln + rng.next(28, 70)
    # island headland, right
    draw.polygon([(x0 + int(w * 0.68), sea_y + 2), (x0 + int(w * 0.80), sea_y - int(h * 0.30)),
                  (x0 + int(w * 0.92), sea_y - int(h * 0.18)), (x1, sea_y - int(h * 0.05)),
                  (x1, sea_y + 2)], fill=(30, 24, 26))
    # a missile launcher on the headland, left of the impact point:
    # a carrier block with two launch tubes angled up, a missile on
    # the rails, and a second missile in flight with a smoke trail —
    # the missile site itself, drawn not implied. The headland is
    # near-black, so the launcher is drawn in pale sand with a dark
    # outline: the previous dark-on-dark version read as a rock.
    lx, ly = x0 + int(w * 0.725), sea_y - int(h * 0.225)
    draw.rectangle([lx - int(w * 0.020), ly, lx + int(w * 0.020),
                    ly + int(h * 0.055)], fill=(216, 208, 186),
                   outline=(30, 24, 26))
    for off in (0, int(h * 0.045)):
        draw.line([(lx - int(w * 0.014), ly + off),
                   (lx + int(w * 0.042), ly - int(h * 0.095) + off)],
                  fill=(232, 226, 210), width=max(4, int(h * 0.04)))
    # missile on the rails: bright body, orange tip
    mx, my = lx + int(w * 0.040), ly - int(h * 0.105)
    draw.line([(mx, my), (mx + int(w * 0.018), my - int(h * 0.042))],
              fill=(250, 250, 246), width=max(4, int(h * 0.035)))
    draw.ellipse([mx + int(w * 0.018) - 3, my - int(h * 0.042) - 3,
                  mx + int(w * 0.018) + 3, my - int(h * 0.042) + 3],
                 fill=(240, 138, 48))
    # missile in flight, arcing from the launcher toward the burst,
    # with a pale smoke trail so the flight reads at card size
    fx1, fy1 = x0 + int(w * 0.79), sea_y - int(h * 0.36)
    for k in range(5):
        t = k / 4
        tx = lx + int(w * 0.045) + (fx1 - lx - int(w * 0.045)) * t
        ty = ly - int(h * 0.12) + (fy1 - ly + int(h * 0.12)) * t \
            - int(h * 0.05) * math.sin(t * math.pi)
        cr = max(2, int(h * (0.018 + 0.012 * t)))
        draw.ellipse([tx - cr, ty - cr, tx + cr, ty + cr],
                     fill=(220, 214, 200))
    draw.line([(fx1 - int(w * 0.012), fy1 + int(h * 0.008)),
               (fx1 + int(w * 0.012), fy1 - int(h * 0.028))],
              fill=(250, 250, 246), width=max(4, int(h * 0.035)))
    draw.ellipse([fx1 + int(w * 0.012) - 3, fy1 - int(h * 0.028) - 3,
                  fx1 + int(w * 0.012) + 3, fy1 - int(h * 0.028) + 3],
                 fill=(240, 138, 48))
    # tanker silhouette, left-centre
    tx, ty = x0 + int(w * 0.30), sea_y - int(h * 0.02)
    tw, th = int(w * 0.30), max(10, int(h * 0.16))
    draw.polygon([(tx, ty), (tx + tw, ty), (tx + tw - int(tw * 0.08), ty + th),
                  (tx + int(tw * 0.05), ty + th)], fill=(12, 12, 14))
    draw.rectangle([tx + int(tw * 0.38), ty - int(th * 0.55),
                    tx + int(tw * 0.55), ty], fill=(12, 12, 14))
    draw.rectangle([tx + int(tw * 0.06), ty - int(th * 0.34),
                    tx + int(tw * 0.30), ty], fill=(12, 12, 14))
    # bridge windows and a funnel, so the silhouette reads as a ship
    for k in range(3):
        wx = tx + int(tw * (0.40 + k * 0.045))
        draw.rectangle([wx, ty - int(th * 0.44), wx + int(tw * 0.025),
                        ty - int(th * 0.30)], fill=(240, 205, 130))
    draw.rectangle([tx + int(tw * 0.60), ty - int(th * 0.62),
                    tx + int(tw * 0.66), ty], fill=(12, 12, 14))
    draw.rectangle([tx + int(tw * 0.60), ty - int(th * 0.62),
                    tx + int(tw * 0.66), ty - int(th * 0.50)],
                   fill=(150, 60, 40))
    # a second tanker, damaged: hull listed to one side, mast broken,
    # smoke rising from its deck — the dek's destruction, shown
    dx, dy = x0 + int(w * 0.56), sea_y + int(h * 0.10)
    dw, dh = int(w * 0.13), max(7, int(h * 0.11))
    draw.polygon([(dx, dy + int(dh * 0.45)), (dx + dw, dy),
                  (dx + dw - int(dw * 0.10), dy + dh),
                  (dx + int(dw * 0.06), dy + dh)], fill=(16, 14, 16))
    draw.line([(dx + int(dw * 0.45), dy + int(dh * 0.2)),
               (dx + int(dw * 0.60), dy - int(h * 0.10))],
              fill=(16, 14, 16), width=2)
    for k in range(3):
        cx = dx + int(dw * (0.55 + k * 0.10))
        cy = dy - int(h * (0.08 + k * 0.09))
        cr = max(3, int(h * (0.045 + k * 0.02)))
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(120, 104, 96))
    # a third tanker, far left and smaller, bow toward the fire —
    # the headline says THREE tankers, so the frame must show three
    fx3, fy3 = x0 + int(w * 0.05), sea_y + int(h * 0.06)
    tw3, th3 = int(w * 0.16), max(7, int(h * 0.11))
    draw.polygon([(fx3, fy3), (fx3 + tw3, fy3),
                  (fx3 + tw3 - int(tw3 * 0.08), fy3 + th3),
                  (fx3 + int(tw3 * 0.05), fy3 + th3)], fill=(12, 12, 14))
    draw.rectangle([fx3 + int(tw3 * 0.40), fy3 - int(th3 * 0.5),
                    fx3 + int(tw3 * 0.55), fy3], fill=(12, 12, 14))
    # flames on the third tanker and on the main tanker: the story
    # is tankers ON FIRE, so at least two hulls must burn visibly
    for _fx, _fy in ((fx3 + int(tw3 * 0.60), fy3 - int(th3 * 0.5)),
                     (tx + int(tw * 0.20), ty - int(th * 0.3)),
                     (tx + int(tw * 0.70), ty - int(th * 0.3))):
        draw.polygon([(_fx - 5, _fy), (_fx, _fy - int(h * 0.14)),
                      (_fx + 5, _fy)], fill=(240, 138, 48))
        draw.polygon([(_fx - 3, _fy), (_fx, _fy - int(h * 0.08)),
                      (_fx + 3, _fy)], fill=(253, 224, 150))
    for k in range(3):
        cx = fx3 + int(tw3 * (0.5 + k * 0.12))
        cy = fy3 - int(h * (0.16 + k * 0.07))
        cr = max(3, int(h * (0.04 + k * 0.015)))
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(120, 104, 96))
    # strike burst at the island's edge: an irregular star flash —
    # a star polygon cannot read as a sun — plus a light-grey smoke
    # column rising from the impact point
    bx, by = x0 + int(w * 0.815), sea_y - int(h * 0.30)
    br = max(6, int(h * 0.10))
    star = []
    ray_rng = LCG(3)
    for k in range(16):
        a = k / 16 * 2 * math.pi
        rl = br * (ray_rng.next(1.15, 1.5) if k % 2 == 0 else
                   ray_rng.next(0.45, 0.6))
        star.append((bx + rl * math.cos(a), by + rl * math.sin(a)))
    draw.polygon(star, fill=(240, 138, 48))
    draw.ellipse([bx - br // 3, by - br // 3, bx + br // 3, by + br // 3],
                 fill=(253, 224, 150))
    for k in range(4):  # smoke: warm grey, overlapping the burst,
        # rising in small steps so it stays attached to the impact
        cx = bx + int(w * (0.004 + k * 0.009))
        cy = by - int(h * (0.10 + k * 0.085))
        cr = max(3, int(h * (0.045 + k * 0.02)))
        # never paint above the scene box: PIL does not clip, and
        # a smoke column over the headline above is a visible defect
        cy = max(cy, y0 + cr + 1)
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(146, 118, 104))


# --------------------------------------------------------------- bridge
def bridge_fallen(draw, box, spec):
    """A strait bridge with its middle span fallen into the water."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (168, 188, 204), (214, 222, 226))
    wat_y = y0 + int(h * 0.62)
    draw.rectangle([x0, wat_y, x1, y1], fill=(52, 84, 110))
    deck_y = y0 + int(h * 0.34)
    # two towers
    for fx in (0.30, 0.70):
        tx = x0 + int(w * fx)
        draw.rectangle([tx - max(3, int(w * 0.012)), y0 + int(h * 0.10),
                        tx + max(3, int(w * 0.012)), wat_y], fill=(70, 74, 80))
    # standing decks from both banks to the towers
    draw.rectangle([x0, deck_y, x0 + int(w * 0.30), deck_y + max(3, int(h * 0.05))],
                   fill=(70, 74, 80))
    draw.rectangle([x0 + int(w * 0.70), deck_y, x1, deck_y + max(3, int(h * 0.05))],
                   fill=(70, 74, 80))
    # cables
    for fx, sx in ((0.30, 0.0), (0.30, 0.52), (0.70, 0.48), (0.70, 1.0)):
        draw.line([(x0 + int(w * fx), y0 + int(h * 0.10)),
                   (x0 + int(w * sx), deck_y)], fill=(90, 96, 104), width=2)
    # the fallen span: tilted deck slab dropping into the strait
    fx0, fy0 = x0 + int(w * 0.34), deck_y + int(h * 0.02)
    fx1, fy1 = x0 + int(w * 0.62), wat_y + int(h * 0.16)
    draw.polygon([(fx0, fy0), (fx1, fy1), (fx1, fy1 + max(4, int(h * 0.07))),
                  (fx0, fy0 + max(4, int(h * 0.07)))], fill=(58, 62, 68))
    # broken end on the right tower side
    draw.polygon([(x0 + int(w * 0.66), deck_y), (x0 + int(w * 0.70), deck_y),
                  (x0 + int(w * 0.665), deck_y + int(h * 0.16))], fill=(58, 62, 68))
    # debris: flat dark fragments riding at the waterline under the
    # gap (flat, so they cannot read as hills or letterforms)
    rng = LCG(7)
    for _ in range(7):
        dx = rng.next(0.38, 0.62) * w + x0
        dy = wat_y + rng.next(1, 5)
        s = rng.next(6, 13)
        draw.rectangle([dx, dy, dx + s, dy + max(2, int(h * 0.03))],
                       fill=(40, 56, 70))
    # ripple lines spreading from the impact point
    for k, rw in enumerate((0.05, 0.10, 0.16)):
        ry = wat_y + int(h * (0.10 + k * 0.09))
        draw.arc([x0 + int(w * (0.575 - rw)), ry - int(h * 0.05),
                  x0 + int(w * (0.575 + rw)), ry + int(h * 0.05)],
                 start=20, end=160, fill=(190, 205, 215), width=2)


# ---------------------------------------------------------------- virus
def virus(draw, box, spec):
    """Outbreak: large spiked virus spheres over a dark field."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(38, 30, 40))
    rng = LCG(99)
    for _ in range(26):  # faint background motes
        mx, my = rng.next(0, w) + x0, rng.next(0, h) + y0
        draw.ellipse([mx, my, mx + 3, my + 3], fill=(74, 62, 80))

    def sphere(cx, cy, r, body, spike):
        for k in range(10):
            a = k / 10 * 2 * math.pi
            ex = cx + (r + r * 0.34) * math.cos(a)
            ey = cy + (r + r * 0.34) * math.sin(a)
            draw.line([(cx, cy), (ex, ey)], fill=spike, width=max(2, r // 6))
            draw.ellipse([ex - r * 0.16, ey - r * 0.16, ex + r * 0.16,
                          ey + r * 0.16], fill=spike)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=body)
        for k in range(4):
            a = k / 4 * 2 * math.pi + 0.4
            dx = cx + r * 0.45 * math.cos(a)
            dy = cy + r * 0.45 * math.sin(a)
            draw.ellipse([dx - r * 0.14, dy - r * 0.14, dx + r * 0.14,
                          dy + r * 0.14], fill=spike)

    sphere(x0 + int(w * 0.30), y0 + int(h * 0.52), max(16, int(h * 0.30)),
           (172, 52, 44), (216, 108, 84))
    sphere(x0 + int(w * 0.62), y0 + int(h * 0.40), max(11, int(h * 0.21)),
           (150, 44, 40), (200, 96, 76))
    sphere(x0 + int(w * 0.82), y0 + int(h * 0.62), max(8, int(h * 0.15)),
           (132, 40, 38), (184, 88, 70))
    if spec.get("label"):
        _label(draw, x0 + int(w * 0.5), y1 - max(13, int(h * 0.16)),
               spec["label"], max(10, int(h * 0.13)), WHITE, bg=(24, 18, 26), box=box)


# -------------------------------------------------------------- cyclone
def cyclone(draw, box, spec):
    """A cyclone from above: spiral arms around a calm eye, over sea."""
    import math
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(44, 84, 112))
    cx, cy = x0 + int(w * 0.44), y0 + int(h * 0.52)
    rmax = int(h * 0.52)
    for arm in range(3):
        base = arm * 2.1
        pts = []
        for k in range(28):
            t = k / 27
            r = 6 + t * rmax
            a = base + t * 3.6
            pts.append((cx + r * math.cos(a), cy + r * 0.72 * math.sin(a)))
        draw.line(pts, fill=(226, 236, 240), width=max(3, int(h * 0.07)))
        pts2 = [(px + 6, py + 4) for px, py in pts]
        draw.line(pts2, fill=(188, 208, 220), width=max(2, int(h * 0.04)))
    draw.ellipse([cx - 9, cy - 7, cx + 9, cy + 7], fill=(30, 62, 88))
    # island chain bottom-right, in the storm's path: irregular
    # land blobs with a palm on the largest, so they read as islands
    for fx, fy, s, palm in ((0.80, 0.74, 13, True), (0.87, 0.82, 9, False),
                            (0.76, 0.86, 7, False)):
        ix, iy = x0 + int(w * fx), y0 + int(h * fy)
        draw.polygon([(ix - s, iy), (ix - s // 2, iy - s // 2),
                      (ix + s // 3, iy - s // 2), (ix + s, iy - 1),
                      (ix + s // 2, iy + s // 2), (ix - s // 3, iy + s // 2)],
                     fill=(96, 128, 92), outline=(60, 84, 58))
        if palm:
            draw.line([(ix, iy - 2), (ix, iy - int(h * 0.16))],
                      fill=(52, 66, 44), width=2)
            for a in (-0.9, -0.3, 0.3, 0.9):
                ex = ix + int(s * 0.9 * math.sin(a))
                ey = iy - int(h * 0.16) + int(s * 0.4 * abs(a))
                draw.line([(ix, iy - int(h * 0.16)), (ex, ey)],
                          fill=(52, 66, 44), width=2)
    if spec.get("label"):
        _label(draw, x0 + int(w * 0.78), y0 + int(h * 0.10), spec["label"],
               max(10, int(h * 0.12)), WHITE, bg=(30, 62, 88), box=box)


# --------------------------------------------------------------- summit
def summit(draw, box, spec):
    """A summit: three leaders seated at one table, shaking hands.

    Composition rules learned from judging: the table is drawn FIRST
    so the leaders sit IN FRONT of it (never floating heads above a
    band); heads are skin tone with hair, torsos are suits in three
    distinct colours; the left and centre leaders reach across and
    clasp hands in front of the table; every name plate carries its
    leader's name — a blank pale rectangle is a defect.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (58, 66, 88), (104, 110, 128))
    for fx in (0.25, 0.5, 0.75):
        px = x0 + int(w * fx)
        draw.line([(px, y0 + 4), (px, y0 + int(h * 0.62))],
                  fill=(84, 92, 110), width=2)
    flags = spec.get("flags", [("CHINA", (178, 34, 34)), ("RUSSIA", (52, 84, 160))])
    n = len(flags)
    for i, (name, col) in enumerate(flags):
        col = tuple(col)
        fx = x0 + int(w * (0.5 + (i - (n - 1) / 2) * 0.32))
        fw, fh = int(w * 0.15), int(h * 0.28)
        fy = y0 + int(h * 0.05)
        draw.rectangle([fx - fw // 2, fy, fx + fw // 2, fy + fh], fill=col,
                       outline=(18, 18, 20), width=2)
        if name.upper() == "CHINA":
            sx, sy = fx - fw // 2 + int(fw * 0.16), fy + int(fh * 0.22)
            _star5(draw, sx, sy, max(3, int(fh * 0.11)), (250, 210, 60))
            for ddx, ddy in ((0.17, -0.08), (0.23, 0.04),
                             (0.23, 0.18), (0.16, 0.30)):
                _star5(draw, sx + int(fw * ddx), sy + int(fh * ddy),
                       max(2, int(fh * 0.06)), (250, 210, 60))
        elif name.upper() == "RUSSIA":
            draw.rectangle([fx - fw // 2, fy, fx + fw // 2,
                            fy + fh // 3], fill=(238, 238, 240))
            draw.rectangle([fx - fw // 2, fy + 2 * fh // 3, fx + fw // 2,
                            fy + fh], fill=(196, 40, 44))
        elif name.upper() == "USA":
            for si in range(7):
                sy0 = fy + si * fh // 7
                sy1 = fy + (si + 1) * fh // 7
                fill = (178, 34, 34) if si % 2 == 0 else (238, 238, 240)
                draw.rectangle([fx - fw // 2 + 2, sy0,
                                fx + fw // 2 - 2, sy1], fill=fill)
            cw, ch = int(fw * 0.40), int(fh * 0.54)
            draw.rectangle([fx - fw // 2 + 2, fy + 2,
                            fx - fw // 2 + cw, fy + ch],
                           fill=(60, 59, 110))
            for gx in range(5):
                for gy in range(4):
                    sx = fx - fw // 2 + int(cw * (0.12 + 0.19 * gx))
                    sy = fy + int(ch * (0.14 + 0.24 * gy))
                    draw.ellipse([sx - 1, sy - 1, sx + 1, sy + 1],
                                 fill=(250, 250, 250))
        _label(draw, fx, fy + fh + 2, name, max(9, int(h * 0.10)), WHITE,
               box=box)
    # the table: straight band, drawn BEFORE the leaders
    table_y = y0 + int(h * 0.68)
    draw.rectangle([x0 + int(w * 0.06), table_y, x0 + int(w * 0.94),
                    table_y + int(h * 0.05)], fill=(150, 118, 76))
    draw.rectangle([x0 + int(w * 0.06), table_y + int(h * 0.05),
                    x0 + int(w * 0.94), y1 - int(h * 0.04)], fill=(96, 70, 44))
    # microphones on the table, one per leader
    for i in range(n):
        fx = 0.5 + (i - (n - 1) / 2) * 0.32
        mx = x0 + int(w * fx) + int(w * 0.07)
        draw.line([(mx, table_y),
                   (mx + int(w * 0.012), table_y - int(h * 0.09))],
                  fill=(20, 18, 18), width=2)
        draw.ellipse([mx + int(w * 0.012) - 3, table_y - int(h * 0.09) - 3,
                      mx + int(w * 0.012) + 3, table_y - int(h * 0.09) + 3],
                     fill=(20, 18, 18))
    # leaders, seated IN FRONT of the table: skin heads with hair,
    # suit torsos in three distinct colours, shirt + tie
    suits = [(38, 48, 72), (52, 52, 56), (72, 60, 46)]
    hairs = [(24, 24, 26), (200, 200, 200), (220, 200, 140)]
    names = {"CHINA": "XI", "RUSSIA": "PUTIN", "USA": "TRUMP"}
    heads = []
    for i, (name, col) in enumerate(flags):
        fx = 0.5 + (i - (n - 1) / 2) * 0.32
        hx = x0 + int(w * fx)
        r = max(7, int(h * 0.125))
        hy = table_y - int(h * 0.115)
        heads.append((hx, hy, r))
        draw.polygon([(hx - int(r * 2.0), hy + int(r * 0.4)),
                      (hx + int(r * 2.0), hy + int(r * 0.4)),
                      (hx + int(r * 2.5), y1), (hx - int(r * 2.5), y1)],
                     fill=suits[i % 3])
        draw.polygon([(hx - int(r * 0.45), hy + int(r * 0.5)),
                      (hx + int(r * 0.45), hy + int(r * 0.5)),
                      (hx, hy + int(r * 1.5))], fill=(238, 236, 230))
        draw.polygon([(hx - 2, hy + int(r * 0.6)), (hx + 2, hy + int(r * 0.6)),
                      (hx + 3, hy + int(r * 1.9)), (hx - 3, hy + int(r * 1.9))],
                     fill=(150, 40, 36))
        draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(222, 190, 158))
        draw.pieslice([hx - r, hy - r, hx + r, hy + r], start=180, end=360,
                      fill=hairs[i % 3])
        # name plate standing on the table in front of the leader —
        # it carries the name, so it is never a blank rectangle
        pw, ph = int(w * 0.085), int(h * 0.13)
        px, py = hx, table_y + int(h * 0.005)
        draw.rectangle([px - pw // 2, py, px + pw // 2, py + ph],
                       fill=(216, 204, 178), outline=(120, 108, 88))
        _label(draw, px, py + 1, names.get(name.upper(), name),
               max(8, int(h * 0.075)), INK, box=box)
    # the handshake: the centre and right leaders — Putin and Trump,
    # the pair the dek says shook hands — reach across and clasp
    # hands ABOVE the table's top edge, against the pale wall;
    # hands drawn on the dark table front read as one black bar.
    # Arms start low on the torso, below the name plates, so they
    # never cross a plate.
    if n >= 3:
        (hx1, hy1, r1), (hx2, hy2, r2) = heads[1], heads[2]
        sx = (hx1 + hx2) // 2
        sy = table_y - int(h * 0.02)
        draw.line([(hx1 + int(r1 * 2.2), hy1 + int(r1 * 2.4)), (sx, sy)],
                  fill=suits[1], width=max(4, int(h * 0.04)))
        draw.line([(hx2 - int(r2 * 2.2), hy2 + int(r2 * 2.4)), (sx, sy)],
                  fill=suits[2], width=max(4, int(h * 0.04)))
        # white cuffs at both wrists, then the clasped hands, large
        # and skin-toned, so the handshake is the thing you see
        draw.rectangle([sx - int(r1 * 1.5), sy - int(r1 * 0.35),
                        sx - int(r1 * 0.9), sy + int(r1 * 0.35)],
                       fill=(238, 236, 230))
        draw.rectangle([sx + int(r1 * 0.9), sy - int(r1 * 0.35),
                        sx + int(r1 * 1.5), sy + int(r1 * 0.35)],
                       fill=(238, 236, 230))
        draw.ellipse([sx - int(r1 * 0.85), sy - int(r1 * 0.6),
                      sx + int(r1 * 0.85), sy + int(r1 * 0.6)],
                     fill=(222, 190, 158), outline=(160, 120, 90))
        draw.ellipse([sx - int(r1 * 0.85), sy - int(r1 * 0.6),
                      sx, sy + int(r1 * 0.6)], fill=(206, 172, 140))


# ---------------------------------------------------------------- chart
# ------------------------------------------------------------- case map
def case_map(draw, box, spec):
    """A clinic: a nurse vaccinates a child; the outbreak map is a
    poster on the wall — the map illustrates the story, it is not
    the whole picture. No Alaska/Hawaii insets are drawn: the old
    ones were invisible at card size, and an undrawn inset is not a
    defect a poster can be faulted for.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(232, 228, 216))
    draw.rectangle([x0, y0 + int(h * 0.82), x1, y1], fill=(190, 182, 168))
    # wall poster, right: a recognisable U.S. outline with case dots
    px0, py0, px1, py1 = (x0 + int(w * 0.63), y0 + int(h * 0.07),
                          x0 + int(w * 0.96), y0 + int(h * 0.66))
    draw.rectangle([px0, py0, px1, py1], fill=(250, 248, 242),
                   outline=(110, 104, 90), width=2)
    _label(draw, (px0 + px1) // 2, py0 + 3,
           spec.get("label", "U.S. MEASLES"), max(9, int(h * 0.10)), INK,
           box=box)
    pts = [(0.08, 0.34), (0.14, 0.22), (0.28, 0.16), (0.38, 0.30),
           (0.46, 0.14), (0.58, 0.16), (0.66, 0.12), (0.78, 0.16),
           (0.88, 0.14), (0.94, 0.24), (0.91, 0.38), (0.85, 0.44),
           (0.87, 0.58), (0.82, 0.74), (0.78, 0.92), (0.74, 0.72),
           (0.66, 0.78), (0.58, 0.68), (0.52, 0.76), (0.44, 0.84),
           (0.38, 0.72), (0.33, 0.80), (0.25, 0.72), (0.17, 0.76),
           (0.11, 0.60), (0.08, 0.46)]
    pw, ph = px1 - px0, py1 - py0
    top = py0 + int(h * 0.16)
    span = int(ph * 0.78)
    poly = [(px0 + int(fx * pw), top + int(fy * span)) for fx, fy in pts]
    draw.polygon(poly, fill=(196, 204, 178), outline=(110, 120, 92))
    rng = LCG(23)
    for _ in range(12):
        fx, fy = rng.next(0.15, 0.85), rng.next(0.25, 0.75)
        dx, dy = px0 + int(fx * pw), top + int(fy * span)
        r = rng.next(2, 4.5)
        draw.ellipse([dx - r, dy - r, dx + r, dy + r], fill=ACCENT)
    hx, hy = px0 + int(0.55 * pw), top + int(0.45 * span)
    draw.ellipse([hx - 6, hy - 6, hx + 6, hy + 6], fill=ACCENT)
    # the bed, left, with the child under a blanket
    bed_y = y0 + int(h * 0.68)
    draw.rectangle([x0 + int(w * 0.05), bed_y, x0 + int(w * 0.52),
                    y0 + int(h * 0.84)], fill=(240, 240, 236),
                   outline=(140, 134, 120))
    draw.rectangle([x0 + int(w * 0.05), bed_y, x0 + int(w * 0.10),
                    y0 + int(h * 0.78)], fill=(250, 250, 246),
                   outline=(140, 134, 120))
    cx, cy = x0 + int(w * 0.14), bed_y - int(h * 0.02)
    cr = max(6, int(h * 0.10))
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(222, 190, 158))
    draw.pieslice([cx - cr, cy - cr, cx + cr, cy + cr], start=180, end=360,
                  fill=(60, 48, 36))
    draw.polygon([(x0 + int(w * 0.20), bed_y), (x0 + int(w * 0.52), bed_y),
                  (x0 + int(w * 0.52), y0 + int(h * 0.84)),
                  (x0 + int(w * 0.20), y0 + int(h * 0.84))],
                 fill=(96, 140, 180))
    # the nurse, standing over the bed, syringe in hand
    nx = x0 + int(w * 0.44)
    nr = max(7, int(h * 0.11))
    ny = y0 + int(h * 0.34)
    draw.polygon([(nx - int(nr * 2.0), ny + int(nr * 0.5)),
                  (nx + int(nr * 2.0), ny + int(nr * 0.5)),
                  (nx + int(nr * 2.3), bed_y), (nx - int(nr * 2.3), bed_y)],
                 fill=(52, 110, 110))
    draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(222, 190, 158))
    draw.pieslice([nx - nr, ny - nr, nx + nr, ny + nr], start=180, end=360,
                  fill=(40, 34, 28))
    draw.rectangle([nx - int(nr * 0.6), ny + int(nr * 0.1),
                    nx + int(nr * 0.6), ny + int(nr * 0.55)],
                   fill=(240, 244, 248))
    # arm + syringe reaching down to the child's arm
    draw.line([(nx - int(nr * 1.2), ny + int(nr * 1.4)),
               (x0 + int(w * 0.20), bed_y - int(h * 0.02))],
              fill=(52, 110, 110), width=max(4, int(h * 0.05)))
    draw.line([(x0 + int(w * 0.20), bed_y - int(h * 0.02)),
               (x0 + int(w * 0.17), bed_y + int(h * 0.02))],
              fill=(200, 200, 204), width=2)


# --------------------------------------------------------------- scales
# ---------------------------------------------------------------- chart
def _chart(draw, box, spec, down=True):
    """A trading floor: a big board with a rising/falling line, and
    the traders below it watching it move.

    The chart is the board on the wall, not the whole picture — the
    scene is the people. (chart_up keeps working: same floor, a
    rising green line instead of a falling red one.)
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    board_y1 = y0 + int(h * 0.55)
    draw.rectangle([x0, y0, x1, board_y1], fill=(16, 22, 34))
    for k in range(1, 4):
        gy = y0 + int(h * 0.55 * k / 4)
        draw.line([(x0 + 6, gy), (x1 - 6, gy)], fill=(52, 62, 80), width=1)
    col = (224, 84, 60) if down else (84, 196, 110)
    if spec.get("ref_label"):
        ry = y0 + int(h * 0.30)
        dash = int(w * 0.035)
        xx = x0 + int(w * 0.05)
        while xx < x1 - int(w * 0.05):
            draw.line([(xx, ry), (min(xx + dash, x1 - int(w * 0.05)), ry)],
                      fill=(232, 178, 84), width=2)
            xx += dash * 2
        _label(draw, x0 + int(w * 0.86), ry - max(11, int(h * 0.13)),
               spec["ref_label"], max(9, int(h * 0.10)), (232, 178, 84),
               box=box)
    pts = []
    n = 9
    for k in range(n):
        t = k / (n - 1)
        base = (0.14 + 0.30 * t) if down else (0.44 - 0.30 * t)
        wiggle = [0, -0.05, 0.03, -0.02, 0.05, -0.04, 0.02, -0.03, 0][k]
        pts.append((x0 + int(w * (0.06 + 0.88 * t)),
                    y0 + int(h * (base + wiggle))))
    draw.line(pts, fill=col, width=max(3, int(h * 0.04)))
    ex, ey = pts[-1]
    ah = max(6, int(h * 0.09))
    if down:
        draw.polygon([(ex, ey + ah), (ex - ah, ey), (ex + 2, ey - 2)], fill=col)
    else:
        draw.polygon([(ex, ey - ah), (ex - ah, ey), (ex + 2, ey + 2)], fill=col)
    if spec.get("label"):
        _label(draw, x0 + int(w * 0.12), y0 + int(h * 0.06), spec["label"],
               max(10, int(h * 0.13)), WHITE, box=box)
    # the floor: a desk band, then three traders in front of the board
    draw.rectangle([x0, board_y1, x1, y1], fill=(58, 52, 46))
    draw.rectangle([x0, board_y1, x1, board_y1 + int(h * 0.05)],
                   fill=(88, 74, 56))
    suits = [(38, 44, 60), (52, 52, 56), (66, 58, 48)]
    for i, fx in enumerate((0.20, 0.50, 0.80)):
        hx = x0 + int(w * fx)
        r = max(6, int(h * 0.095))
        hy = board_y1 + int(h * 0.16)
        draw.polygon([(hx - int(r * 2.0), hy + int(r * 0.5)),
                      (hx + int(r * 2.0), hy + int(r * 0.5)),
                      (hx + int(r * 2.4), y1), (hx - int(r * 2.4), y1)],
                     fill=suits[i])
        draw.polygon([(hx - int(r * 0.4), hy + int(r * 0.55)),
                      (hx + int(r * 0.4), hy + int(r * 0.55)),
                      (hx, hy + int(r * 1.4))], fill=(238, 236, 230))
        draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(222, 190, 158))
        draw.pieslice([hx - r, hy - r, hx + r, hy + r], start=180, end=360,
                      fill=(40, 34, 28) if i != 2 else (150, 150, 150))
    # middle trader points up at the falling board; left trader holds
    # a phone to his ear
    hx = x0 + int(w * 0.50)
    hy = board_y1 + int(h * 0.16)
    r = max(6, int(h * 0.095))
    draw.line([(hx + int(r * 1.6), hy + int(r * 1.2)),
               (hx + int(w * 0.10), y0 + int(h * 0.30))],
              fill=suits[1], width=max(4, int(h * 0.05)))
    draw.ellipse([hx + int(w * 0.10) - 4, y0 + int(h * 0.30) - 4,
                  hx + int(w * 0.10) + 4, y0 + int(h * 0.30) + 4],
                 fill=(222, 190, 158))
    hx = x0 + int(w * 0.20)
    draw.rectangle([hx - int(r * 0.6), hy - int(r * 0.4),
                    hx + int(r * 0.2), hy + int(r * 0.5)], fill=(20, 20, 22))


# ----------------------------------------------------------------- chip
def chart_down(draw, box, spec):
    _chart(draw, box, spec, down=True)


def chart_up(draw, box, spec):
    _chart(draw, box, spec, down=False)


# ----------------------------------------------------------------- chip
def chip(draw, box, spec):
    """A chip fab: a cleanroom worker holds up a glowing wafer.

    The chip is an object in someone's hands, not a diagram — the
    scene is the fab floor around it.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (36, 42, 52), (70, 78, 90))
    # ceiling light bars
    for fx in (0.18, 0.50, 0.82):
        lx = x0 + int(w * fx)
        draw.rectangle([lx - int(w * 0.10), y0 + int(h * 0.04),
                        lx + int(w * 0.10), y0 + int(h * 0.09)],
                       fill=(230, 234, 240))
    # machine cabinets along the back wall
    for fx, fw in ((0.02, 0.20), (0.78, 0.20)):
        mx = x0 + int(w * fx)
        draw.rectangle([mx, y0 + int(h * 0.42), mx + int(w * fw),
                        y0 + int(h * 0.86)], fill=(28, 34, 40),
                       outline=(90, 100, 112))
        for k in range(3):
            ly = y0 + int(h * (0.50 + k * 0.10))
            draw.ellipse([mx + int(w * 0.03), ly, mx + int(w * 0.03) + 5,
                          ly + 5],
                         fill=(120, 190, 210) if k != 1 else (240, 180, 80))
    draw.rectangle([x0, y0 + int(h * 0.86), x1, y1], fill=(52, 58, 66))
    # second worker, smaller, background right, carrying a wafer box
    bx, by = x0 + int(w * 0.66), y0 + int(h * 0.62)
    br = max(5, int(h * 0.07))
    draw.polygon([(bx - int(br * 1.8), by + int(br * 0.4)),
                  (bx + int(br * 1.8), by + int(br * 0.4)),
                  (bx + int(br * 2.1), y0 + int(h * 0.86)),
                  (bx - int(br * 2.1), y0 + int(h * 0.86))],
                 fill=(210, 214, 220))
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(226, 230, 236))
    draw.ellipse([bx - int(br * 0.6), by - int(br * 0.2),
                  bx + int(br * 0.6), by + int(br * 0.5)],
                 fill=(222, 190, 158))
    # main worker, centre-left, white bunny suit, holding the wafer up
    hx, hy = x0 + int(w * 0.40), y0 + int(h * 0.42)
    r = max(8, int(h * 0.13))
    draw.polygon([(hx - int(r * 2.2), hy + int(r * 0.5)),
                  (hx + int(r * 2.2), hy + int(r * 0.5)),
                  (hx + int(r * 2.6), y1), (hx - int(r * 2.6), y1)],
                 fill=(232, 236, 240))
    draw.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(240, 244, 248))
    draw.ellipse([hx - int(r * 0.55), hy - int(r * 0.15),
                  hx + int(r * 0.55), hy + int(r * 0.55)],
                 fill=(222, 190, 158))
    # the wafer: a glowing disc held up at chest height, grid etched
    wx, wy = hx + int(w * 0.16), hy + int(h * 0.22)
    wr = max(10, int(h * 0.19))
    draw.ellipse([wx - wr, wy - wr, wx + wr, wy + wr],
                 fill=(120, 190, 210), outline=(220, 240, 248), width=2)
    for k in (-1, 0, 1):
        draw.line([(wx - wr + 3, wy + k * wr // 2),
                   (wx + wr - 3, wy + k * wr // 2)], fill=(220, 240, 248),
                  width=1)
        draw.line([(wx + k * wr // 2, wy - wr + 3),
                   (wx + k * wr // 2, wy + wr - 3)], fill=(220, 240, 248),
                  width=1)
    # gloved hands on the wafer's edge
    for sgn in (-1, 1):
        gx = wx + sgn * int(wr * 0.95)
        draw.ellipse([gx - 5, wy - 4, gx + 5, wy + 4], fill=(240, 244, 248))
    if spec.get("label"):
        _label(draw, x0 + int(w * 0.14), y0 + int(h * 0.14), spec["label"],
               max(10, int(h * 0.13)), WHITE, bg=(24, 30, 36), box=box)


# --------------------------------------------------------------- ballot
# -------------------------------------------------------------- missiles
def missiles(draw, box, spec):
    """Night coast: three missile trails rising from launch points."""
    import math
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (10, 14, 30), (38, 48, 74))
    rng = LCG(5)
    for _ in range(22):
        sx, sy = rng.next(0, w) + x0, rng.next(0, 0.5 * h) + y0
        draw.ellipse([sx, sy, sx + 2, sy + 2], fill=(200, 208, 224))
    ground_y = y0 + int(h * 0.86)
    draw.polygon([(x0, y1), (x0, ground_y), (x0 + int(w * 0.3), ground_y - int(h * 0.06)),
                  (x0 + int(w * 0.62), ground_y + int(h * 0.02)),
                  (x0 + int(w * 0.85), ground_y - int(h * 0.05)), (x1, ground_y),
                  (x1, y1)], fill=(16, 20, 26))
    # near-vertical, staggered trails from three separate launchers:
    # the old parallel gold arcs read as a rainbow, not as launches
    for ti, (fx, rise, drift) in enumerate(((0.18, 0.82, 0.04),
                                            (0.48, 0.90, -0.05),
                                            (0.74, 0.68, 0.09))):
        lx, ly = x0 + int(w * fx), ground_y - int(h * 0.04)
        # a launcher at the base, so the trail starts from hardware
        draw.rectangle([lx - int(w * 0.02), ly - int(h * 0.02),
                        lx + int(w * 0.02), ly + int(h * 0.03)],
                       fill=(40, 46, 54))
        draw.line([(lx - int(w * 0.01), ly - int(h * 0.02)),
                   (lx + int(w * 0.02), ly - int(h * 0.10))],
                  fill=(70, 78, 90), width=3)
        ex, ey = lx + int(w * drift), y0 + int(h * (0.86 - rise))
        # a rising, steepening curve: control point above the launch
        cxp, cyp = lx + int(w * drift * 0.25), ly - int(h * rise * 0.55)
        pts = []
        for k in range(19):
            t = k / 18
            px = (1 - t) ** 2 * lx + 2 * (1 - t) * t * cxp + t * t * ex
            py = (1 - t) ** 2 * ly + 2 * (1 - t) * t * cyp + t * t * ey
            pts.append((px, py))
        draw.line(pts, fill=(240, 190, 110), width=max(2, int(h * 0.03)))
        draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 230, 160))
        # smoke puffs along the middle trail only: one trail with a
        # smoke wake breaks the three-parallel-arcs reading entirely
        if ti == 1:
            for k in (3, 6, 9, 12):
                sx, sy = pts[k]
                sr = max(2, int(h * 0.03))
                draw.ellipse([sx - sr - 4, sy - sr, sx - sr + 4, sy + sr],
                             fill=(140, 140, 150))
        # launch flash at the base
        for dx in (-6, 0, 6):
            draw.line([(lx, ly), (lx + dx, ly - int(h * 0.10))],
                      fill=(250, 200, 120), width=2)


# ---------------------------------------------------------------- crash
def crash(draw, box, spec):
    """A crashed aircraft on snowy terrain, smoke still rising."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (150, 164, 178), (226, 230, 232))
    g_y = y0 + int(h * 0.66)
    draw.polygon([(x0, y1), (x0, g_y + int(h * 0.08)),
                  (x0 + int(w * 0.4), g_y - int(h * 0.05)),
                  (x0 + int(w * 0.75), g_y + int(h * 0.06)), (x1, g_y),
                  (x1, y1)], fill=(238, 240, 242))
    # fuselage, nose down, broken tail — near-black for contrast
    fx, fy = x0 + int(w * 0.30), g_y - int(h * 0.10)
    fl = int(w * 0.36)
    draw.polygon([(fx, fy), (fx + fl, fy + int(h * 0.13)),
                  (fx + fl - int(fl * 0.06), fy + int(h * 0.20)),
                  (fx + int(fl * 0.08), fy + int(h * 0.10))], fill=(26, 28, 32))
    draw.polygon([(fx + int(fl * 0.06), fy - int(h * 0.02)),
                  (fx + int(fl * 0.16), fy - int(h * 0.16)),
                  (fx + int(fl * 0.22), fy)], fill=(26, 28, 32))
    draw.polygon([(fx + int(fl * 0.40), fy + int(h * 0.06)),
                  (fx + int(fl * 0.62), fy + int(h * 0.20)),
                  (fx + int(fl * 0.50), fy + int(h * 0.22))], fill=(20, 22, 26))
    # smoke: a wind-blown plume — small puffs trailing up and to the
    # right, not a stacked column (a column read as a falling bomb)
    rng = LCG(31)
    for k in range(7):
        sx = fx + int(fl * 0.55) + k * int(w * 0.045)
        sy = fy - int(h * 0.01) - k * int(h * 0.055)
        r = int(h * (0.045 + k * 0.011))
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(70, 74, 80))
    # debris trail
    for k in range(6):
        dx = fx + fl + int(w * 0.04 * k)
        dy = g_y + int(h * 0.05) + (k % 2) * int(h * 0.05)
        draw.rectangle([dx, dy, dx + int(w * 0.02), dy + 3], fill=(70, 74, 80))


# ---------------------------------------------------------------- probe
def probe(draw, box, spec):
    """Deep space: a probe with a great dish, signalling a distant Earth."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(6, 8, 16))
    rng = LCG(77)
    for _ in range(40):
        sx, sy = rng.next(0, w) + x0, rng.next(0, h) + y0
        s = rng.next(1, 2.6)
        draw.ellipse([sx, sy, sx + s, sy + s], fill=(210, 218, 235))
    # Earth, small and far, right
    ex, ey = x0 + int(w * 0.86), y0 + int(h * 0.30)
    er = max(7, int(h * 0.13))
    draw.ellipse([ex - er, ey - er, ex + er, ey + er], fill=(86, 140, 200))
    draw.ellipse([ex - er // 2, ey - er // 3, ex, ey + er // 4],
                 fill=(96, 168, 110))
    # the probe: bus, boom, and the great dish facing Earth
    bx, by = x0 + int(w * 0.30), y0 + int(h * 0.55)
    draw.rectangle([bx - int(w * 0.05), by - int(h * 0.10),
                    bx + int(w * 0.05), by + int(h * 0.10)], fill=(168, 172, 180))
    dr = int(h * 0.34)
    draw.pieslice([bx + int(w * 0.02), by - dr, bx + int(w * 0.02) + 2 * dr,
                   by + dr], start=90, end=270, fill=(216, 220, 226))
    draw.line([(bx, by), (bx + int(w * 0.16), by - int(h * 0.30))],
              fill=(168, 172, 180), width=3)
    draw.ellipse([bx + int(w * 0.16) - 3, by - int(h * 0.30) - 3,
                  bx + int(w * 0.16) + 3, by - int(h * 0.30) + 3],
                 fill=(216, 220, 226))
    # signal arcs from dish toward Earth
    for k in range(3):
        r = int(h * (0.16 + k * 0.13))
        draw.arc([bx + int(w * 0.10) - r // 3, by - r, bx + int(w * 0.10) + r,
                  by + r], start=-52, end=52, fill=(240, 205, 105), width=2)
    if spec.get("label"):
        _label(draw, x0 + int(w * 0.30), y1 - max(13, int(h * 0.16)),
               spec["label"], max(10, int(h * 0.12)), (220, 226, 240), box=box)


# --------------------------------------------------------------- ballot
def ballot(draw, box, spec):
    """The House chamber: rows of seats, raised hands, the rostrum.

    The vote is people in a room, not a ballot paper — raised hands
    and the speaker's rostrum are the vote, shown.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (96, 78, 56), (150, 126, 92))
    # curved rows of desks with seated members
    for row, ry, n in ((0, 0.62, 9), (1, 0.80, 11)):
        dy = y0 + int(h * ry)
        draw.rectangle([x0 + int(w * 0.04), dy, x1 - int(w * 0.04),
                        dy + int(h * 0.07)], fill=(70, 52, 36))
        for k in range(n):
            mx = x0 + int(w * (0.08 + 0.84 * k / (n - 1)))
            hr = max(4, int(h * 0.055))
            hy = dy - int(h * 0.06)
            draw.ellipse([mx - hr, hy - hr, mx + hr, hy + hr],
                         fill=(222, 190, 158) if k % 3 else (190, 150, 120))
            draw.pieslice([mx - hr, hy - hr, mx + hr, hy + hr],
                          start=180, end=360,
                          fill=(40, 34, 28) if k % 2 else (90, 78, 60))
    # the rostrum, centre, with the speaker behind it
    px0, px1 = x0 + int(w * 0.38), x0 + int(w * 0.62)
    py0, py1 = y0 + int(h * 0.30), y0 + int(h * 0.58)
    draw.rectangle([px0, py0, px1, py1], fill=(52, 40, 28),
                   outline=(30, 22, 16))
    draw.rectangle([px0, py0, px1, py0 + int(h * 0.04)], fill=(120, 96, 64))
    sx, sy = x0 + w // 2, py0 - int(h * 0.02)
    sr = max(6, int(h * 0.09))
    draw.polygon([(sx - int(sr * 2.0), sy + int(sr * 0.4)),
                  (sx + int(sr * 2.0), sy + int(sr * 0.4)),
                  (sx + int(sr * 2.2), py0), (sx - int(sr * 2.2), py0)],
                 fill=(26, 26, 30))
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(222, 190, 158))
    draw.pieslice([sx - sr, sy - sr, sx + sr, sy + sr], start=180, end=360,
                  fill=(150, 150, 150))
    # raised hands from the seats, in front of the rostrum: arms up
    rng = LCG(11)
    for k in range(5):
        mx = x0 + int(w * (0.12 + k * 0.17))
        base_y = y0 + int(h * 0.62)
        tip_y = base_y - int(h * (0.16 + rng.next(0, 0.08)))
        draw.line([(mx, base_y), (mx + 4, tip_y)], fill=(222, 190, 158),
                  width=max(3, int(h * 0.035)))
        draw.ellipse([mx + 1, tip_y - 5, mx + 7, tip_y + 1],
                     fill=(222, 190, 158))
    if spec.get("label"):
        _label(draw, x0 + int(w * 0.5), y0 + int(h * 0.06), spec["label"],
               max(10, int(h * 0.12)), (240, 220, 170), box=box)


# -------------------------------------------------------------- case_map
# ---------------------------------------------------------------- gavel
def gavel(draw, box, spec):
    """A court: pediment and columns, a gavel striking its block."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    draw.rectangle(box, fill=(206, 198, 178))
    # pediment + columns
    draw.polygon([(x0 + int(w * 0.08), y0 + int(h * 0.30)),
                  (x0 + int(w * 0.5), y0 + int(h * 0.08)),
                  (x0 + int(w * 0.92), y0 + int(h * 0.30))], fill=(120, 108, 88))
    for fx in (0.16, 0.34, 0.52, 0.70, 0.86):
        cx = x0 + int(w * fx)
        draw.rectangle([cx - int(w * 0.025), y0 + int(h * 0.34),
                        cx + int(w * 0.025), y0 + int(h * 0.78)],
                       fill=(228, 220, 200), outline=(140, 130, 108))
    draw.rectangle([x0 + int(w * 0.06), y0 + int(h * 0.78),
                    x0 + int(w * 0.94), y0 + int(h * 0.84)], fill=(120, 108, 88))
    # gavel: an oversized mallet — horizontal cylinder head with end
    # caps, long handle down to the block (at card size a small
    # gavel read as a cannon; this one cannot)
    block_top = y0 + int(h * 0.86)
    draw.rectangle([x0 + int(w * 0.40), block_top,
                    x0 + int(w * 0.76), y0 + int(h * 0.94)], fill=(120, 84, 44),
                   outline=(70, 48, 24), width=2)
    gx, gy = x0 + int(w * 0.58), block_top - int(h * 0.02)
    hw, hh = int(w * 0.34), int(h * 0.17)
    draw.line([(gx, gy), (gx + int(w * 0.15), gy - int(h * 0.34))],
              fill=(96, 66, 36), width=max(5, int(h * 0.06)))
    draw.rectangle([gx - hw // 2, gy - hh, gx + hw // 2, gy], fill=(120, 84, 44),
                   outline=(70, 48, 24), width=2)
    draw.rectangle([gx - hw // 2, gy - hh, gx - hw // 2 + int(hw * 0.16), gy],
                   fill=(86, 58, 30))
    draw.rectangle([gx + hw // 2 - int(hw * 0.16), gy - hh, gx + hw // 2, gy],
                   fill=(86, 58, 30))
    # impact ticks between head and block
    for dx in (-20, 0, 20):
        draw.line([(gx + dx, gy + 2), (gx + dx, gy + 10)], fill=INK, width=2)


# --------------------------------------------------------------- scales
def scales(draw, box, spec):
    """A courtroom: three judges on the bench, the scales small on
    the bench front — the court is the scene, the scales its emblem.
    """
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (104, 86, 64), (150, 128, 96))
    # wall seal behind the chief judge
    cx, cy = x0 + w // 2, y0 + int(h * 0.20)
    cr = max(8, int(h * 0.15))
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr],
                 fill=(198, 148, 42), outline=(120, 96, 40), width=2)
    draw.ellipse([cx - int(cr * 0.6), cy - int(cr * 0.6),
                  cx + int(cr * 0.6), cy + int(cr * 0.6)],
                 fill=(150, 116, 52))
    # the bench
    bench_y = y0 + int(h * 0.60)
    draw.rectangle([x0 + int(w * 0.04), bench_y, x0 + int(w * 0.96),
                    y0 + int(h * 0.88)], fill=(70, 52, 36))
    draw.rectangle([x0 + int(w * 0.04), bench_y, x0 + int(w * 0.96),
                    bench_y + int(h * 0.04)], fill=(120, 96, 64))
    # three judges seated behind the bench
    for i, fx in enumerate((0.22, 0.50, 0.78)):
        jx = x0 + int(w * fx)
        jr = max(7, int(h * 0.10))
        jy = bench_y - int(h * 0.10)
        draw.polygon([(jx - int(jr * 2.1), jy + int(jr * 0.4)),
                      (jx + int(jr * 2.1), jy + int(jr * 0.4)),
                      (jx + int(jr * 2.4), bench_y),
                      (jx - int(jr * 2.4), bench_y)], fill=(26, 26, 30))
        draw.ellipse([jx - jr, jy - jr, jx + jr, jy + jr],
                     fill=(222, 190, 158))
        hair = (200, 200, 200) if i == 1 else (60, 52, 44)
        draw.pieslice([jx - jr, jy - jr, jx + jr, jy + jr], start=180,
                      end=360, fill=hair)
        draw.polygon([(jx - int(jr * 0.4), jy + int(jr * 0.55)),
                      (jx + int(jr * 0.4), jy + int(jr * 0.55)),
                      (jx, jy + int(jr * 1.3))], fill=(240, 240, 236))
    # the scales, small and gold, centred on the bench front
    sx, sy = x0 + w // 2, bench_y + int(h * 0.16)
    draw.line([(sx, sy - int(h * 0.06)), (sx, sy + int(h * 0.06))],
              fill=(198, 148, 42), width=3)
    draw.line([(sx - int(w * 0.07), sy - int(h * 0.04)),
               (sx + int(w * 0.07), sy - int(h * 0.04))],
              fill=(198, 148, 42), width=3)
    for sgn in (-1, 1):
        px = sx + sgn * int(w * 0.07)
        pan_y = sy + int(h * 0.02)
        draw.line([(px, sy - int(h * 0.04)), (px - 6, pan_y)],
                  fill=(198, 148, 42), width=2)
        draw.line([(px, sy - int(h * 0.04)), (px + 6, pan_y)],
                  fill=(198, 148, 42), width=2)
        draw.pieslice([px - 8, pan_y - 3, px + 8, pan_y + 5], start=0,
                      end=180, fill=(198, 148, 42))
    # counsel standing at the left, facing the bench, papers in hand
    lx = x0 + int(w * 0.10)
    lr = max(5, int(h * 0.07))
    ly = y0 + int(h * 0.88)
    draw.polygon([(lx - int(lr * 1.8), ly - int(h * 0.22)),
                  (lx + int(lr * 1.8), ly - int(h * 0.22)),
                  (lx + int(lr * 2.0), y1), (lx - int(lr * 2.0), y1)],
                 fill=(40, 40, 46))
    draw.ellipse([lx - lr, ly - int(h * 0.22) - lr,
                  lx + lr, ly - int(h * 0.22) + lr], fill=(222, 190, 158))
# -------------------------------------------------------------- generic
def tents(draw, box, spec):
    """A camp of tents under falling snow (displacement + winter)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    gradient(draw, x0, y0, x1, y1, (96, 110, 128), (196, 204, 210))
    gy = y0 + int(h * 0.70)
    draw.rectangle([x0, gy, x1, y1], fill=(232, 236, 238))
    for fx, s in ((0.16, 0.30), (0.44, 0.38), (0.74, 0.30)):
        tx, tw = x0 + int(w * fx), int(w * s)
        th = int(h * 0.34)
        draw.polygon([(tx, gy), (tx + tw // 2, gy - th), (tx + tw, gy)],
                     fill=(176, 168, 150), outline=(110, 102, 88))
        # door flap: a darker triangle with a centre seam, so the
        # shape reads as a tent entrance, not a bare pyramid
        draw.polygon([(tx + tw // 2 - int(tw * 0.10), gy),
                      (tx + tw // 2, gy - int(th * 0.52)),
                      (tx + tw // 2 + int(tw * 0.10), gy)], fill=(70, 64, 54))
        draw.line([(tx + tw // 2, gy - int(th * 0.52)),
                   (tx + tw // 2, gy)], fill=(232, 228, 218), width=2)
        # guy ropes from the apex to pegs on both sides
        for side in (-1, 1):
            px = tx + tw // 2 + side * int(tw * 0.62)
            draw.line([(tx + tw // 2, gy - th + 2), (px, gy + 2)],
                      fill=(90, 84, 72), width=2)
            draw.ellipse([px - 2, gy, px + 2, gy + 4], fill=(70, 64, 54))
        # ground shadow so the tent sits on the snow, not floats
        draw.line([(tx - 3, gy + 2), (tx + tw + 3, gy + 2)],
                  fill=(180, 186, 190), width=2)
    rng = LCG(13)
    for _ in range(30):
        sx, sy = rng.next(0, w) + x0, rng.next(0, 0.8 * h) + y0
        draw.ellipse([sx, sy, sx + 3, sy + 3], fill=WHITE)


PAINTERS = {
    "sea_strike": sea_strike,
    "bridge_fallen": bridge_fallen,
    "virus": virus,
    "cyclone": cyclone,
    "summit": summit,
    "case_map": case_map,
    "chart_down": chart_down,
    "chart_up": chart_up,
    "chip": chip,
    "missiles": missiles,
    "crash": crash,
    "probe": probe,
    "ballot": ballot,
    "gavel": gavel,
    "scales": scales,
    "tents": tents,
}
