"""Parametric scene painters for the front page.

Each painter receives (draw, x, y, w, h, spec) and fills its box with
bold flat shapes - one actor, one setting, one action - drawn to stay
recognisable when the whole page is shrunk to letterbox scale. Any
scatter (stars, spray) comes from a fixed-seed LCG local to the call,
so renders are byte-identical run after run.
"""

import math

from PIL import ImageFont

from .textutil import SANS_BOLD, width_of

INK = (26, 24, 22)
PAPER = (247, 243, 234)


class Lcg:
    """Tiny linear congruential generator with a fixed seed."""

    def __init__(self, seed):
        self.state = seed & 0x7FFFFFFF

    def next(self):
        self.state = (self.state * 1103515245 + 12345) & 0x7FFFFFFF
        return self.state

    def below(self, n):
        return self.next() % n


def label_chip(draw, x, y, w, h, text, size=11, align="tl",
               bg=(20, 20, 24), fg=(245, 242, 235)):
    """A small dark caption chip, always clamped fully inside the box."""
    fnt = ImageFont.truetype(SANS_BOLD, size)
    tw = width_of(text, fnt)
    cw = tw + 10
    ch = size + 7
    if align == "tr":
        cx = x + w - cw - 4
    elif align == "br":
        cx = x + w - cw - 4
    else:
        cx = x + 4
    cy = y + h - ch - 4 if align in ("br", "bl") else y + 4
    cx = max(x + 2, min(cx, x + w - cw - 2))
    cy = max(y + 2, min(cy, y + h - ch - 2))
    draw.rectangle([cx, cy, cx + cw, cy + ch], fill=bg)
    draw.text((cx + 5, cy + 3), text, font=fnt, fill=fg)


def person(draw, cx, top, scale, skin, hair, suit, tie=(150, 30, 30)):
    """A simple seated/standing figure: head with hair cap, torso, tie."""
    r = max(4, int(7 * scale))
    draw.ellipse([cx - r, top, cx + r, top + 2 * r], fill=skin)
    draw.pieslice([cx - r, top - 1, cx + r, top + 2 * r], 180, 360, fill=hair)
    tw = int(13 * scale)
    th = int(16 * scale)
    draw.rectangle([cx - tw, top + 2 * r - 1, cx + tw, top + 2 * r + th], fill=suit)
    shirt_w = max(2, int(3 * scale))
    draw.rectangle([cx - shirt_w, top + 2 * r - 1, cx + shirt_w,
                    top + 2 * r + th], fill=(240, 238, 230))
    draw.polygon([(cx - 2, top + 2 * r + 1), (cx + 2, top + 2 * r + 1),
                  (cx, top + 2 * r + int(7 * scale))], fill=tie)
    return top + 2 * r + th


def star_burst(draw, cx, cy, radius, fill, seed=7):
    """A jagged irregular burst: alternating long/short spikes, never a
    round disc (a disc reads as a second sun)."""
    rng = Lcg(seed)
    pts = []
    spikes = 11
    for i in range(spikes * 2):
        ang = math.pi * i / spikes
        rad = radius if i % 2 == 0 else radius * (0.38 + 0.2 * (rng.below(10) / 10.0))
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def flame(draw, bx, by, s, seed=3):
    """A small teardrop flame: orange body, yellow core."""
    draw.polygon([(bx - s, by), (bx, by - int(2.6 * s)), (bx + s, by)], fill=(232, 110, 20))
    draw.polygon([(bx - s // 2, by), (bx, by - int(1.5 * s)), (bx + s // 2, by)],
                 fill=(250, 190, 60))


def tanker(draw, x, y, w, hull=(40, 44, 54), deck=(120, 40, 36)):
    """A tanker silhouette: hull, deck line, bridge block, funnel."""
    h = max(8, w // 7)
    draw.polygon([(x, y), (x + w, y), (x + w - h, y + h), (x + h, y + h)], fill=hull)
    draw.rectangle([x + 2, y - 3, x + w - 2, y], fill=deck)
    bw = max(6, w // 8)
    draw.rectangle([x + w - bw - 6, y - 3 - h, x + w - 6, y - 3], fill=(225, 222, 214))
    for i in range(3):
        draw.rectangle([x + w - bw - 4 + i * 3, y - 3 - h + 2,
                        x + w - bw - 3 + i * 3, y - 3 - h + 4], fill=(250, 210, 90))
    draw.rectangle([x + w // 3, y - 3 - h // 2, x + w // 3 + 4, y - 3], fill=(30, 30, 34))


def smoke(draw, x, y, s, tone=(168, 160, 150)):
    """Attached lightened smoke: overlapping soft-grey ellipses."""
    draw.ellipse([x, y - s, x + 2 * s, y + s], fill=tone)
    draw.ellipse([x + s, y - int(1.7 * s), x + 3 * s, y], fill=(188, 180, 170))
    draw.ellipse([x + int(1.8 * s), y - int(2.3 * s), x + int(3.4 * s), y - s],
                 fill=(205, 198, 188))


# ---------------------------------------------------------------- scenes

def paint_sea_strike(draw, x, y, w, h, spec):
    # Dusk sky over a strait; island headland on the right.
    draw.rectangle([x, y, x + w, y + h], fill=(52, 62, 92))
    draw.rectangle([x, y, x + w, y + int(h * 0.42)], fill=(196, 96, 52))
    draw.rectangle([x, y, x + w, y + int(h * 0.22)], fill=(120, 66, 66))
    sea_y = y + int(h * 0.58)
    draw.rectangle([x, sea_y, x + w, y + h], fill=(36, 74, 96))
    # One small half-disc sun low on the horizon.
    sun_r = max(6, h // 9)
    draw.pieslice([x + int(w * 0.30) - sun_r, sea_y - sun_r,
                   x + int(w * 0.30) + sun_r, sea_y + sun_r], 180, 360,
                  fill=(250, 205, 110))
    # Island headland, kept high and behind the third hull.
    draw.polygon([(x + int(w * 0.70), sea_y), (x + int(w * 0.82), y + int(h * 0.28)),
                  (x + int(w * 0.94), y + int(h * 0.32)), (x + w, sea_y)], fill=(38, 40, 38))
    # Three tankers, each hull fully separated by open water and each
    # carrying its own flame plume, so all three stay countable.
    tanker(draw, x + int(w * 0.03), sea_y + int(h * 0.08), int(w * 0.16))
    flame(draw, x + int(w * 0.09), sea_y + int(h * 0.04), 4)
    smoke(draw, x + int(w * 0.10), sea_y + int(h * 0.01), 3)
    tanker(draw, x + int(w * 0.30), sea_y + int(h * 0.14), int(w * 0.28))
    flame(draw, x + int(w * 0.44), sea_y + int(h * 0.08), 6)
    smoke(draw, x + int(w * 0.44), sea_y + int(h * 0.02), 5)
    star_burst(draw, x + int(w * 0.80), y + int(h * 0.24), max(7, h // 8),
               (255, 150, 40), seed=11)
    tanker(draw, x + int(w * 0.68), sea_y + int(h * 0.24), int(w * 0.20))
    flame(draw, x + int(w * 0.78), sea_y + int(h * 0.18), 5)
    smoke(draw, x + int(w * 0.79), sea_y + int(h * 0.12), 4)
    # Shore missile launcher, bottom-left foreground.
    lx, ly = x + int(w * 0.05), y + h - 6
    draw.rectangle([lx, ly - 6, lx + 20, ly], fill=(24, 26, 24))
    draw.line([lx + 4, ly - 6, lx + 16, ly - 18], fill=(24, 26, 24), width=3)
    draw.rectangle([lx + 13, ly - 22, lx + 21, ly - 15], fill=(60, 62, 58))


def paint_bridge_fallen(draw, x, y, w, h, spec):
    draw.rectangle([x, y, x + w, y + h], fill=(168, 196, 208))
    water_y = y + int(h * 0.68)
    draw.rectangle([x, water_y, x + w, y + h], fill=(70, 110, 138))
    deck_y = y + int(h * 0.40)
    tower_x = [x + int(w * 0.16), x + int(w * 0.80)]
    for tx in tower_x:
        draw.rectangle([tx, y + int(h * 0.10), tx + 7, water_y], fill=(70, 76, 84))
    # Suspension cables on the standing parts only.
    draw.line([x, deck_y - 4, tower_x[0] + 3, y + int(h * 0.12)], fill=(50, 54, 60), width=2)
    draw.line([tower_x[1] + 3, y + int(h * 0.12), x + w, deck_y - 4], fill=(50, 54, 60), width=2)
    # Standing deck stubs and the fallen middle span, tilted into the water.
    draw.rectangle([x, deck_y, tower_x[0] + 40, deck_y + 6], fill=(52, 56, 64))
    draw.rectangle([tower_x[1] - 34, deck_y, x + w, deck_y + 6], fill=(52, 56, 64))
    mid_x = x + int(w * 0.40)
    draw.polygon([(mid_x, deck_y + 2), (mid_x + int(w * 0.22), deck_y + 10),
                  (mid_x + int(w * 0.22), deck_y + 16), (mid_x, deck_y + 8)],
                 fill=(52, 56, 64))
    # Flat debris fragments at the waterline plus ripple arcs.
    rng = Lcg(23)
    for i in range(7):
        dx = mid_x - 14 + rng.below(int(w * 0.30))
        dy = water_y + 2 + rng.below(5)
        draw.rectangle([dx, dy, dx + 7, dy + 3], fill=(88, 96, 104))
    for r in (10, 18, 26):
        draw.arc([mid_x + 16 - r, water_y - r // 3, mid_x + 16 + r, water_y + r // 2],
                 0, 180, fill=(210, 226, 234), width=2)


def paint_clinic_ward(draw, x, y, w, h, spec):
    # Ebola treatment ward: pale wall, floor, a red-cross sign, two
    # responders in protective suits and three occupied beds.
    draw.rectangle([x, y, x + w, y + h], fill=(226, 222, 206))
    floor_y = y + int(h * 0.74)
    draw.rectangle([x, floor_y, x + w, y + h], fill=(176, 168, 148))
    # Red-cross sign on the back wall.
    sx, sy = x + int(w * 0.47), y + int(h * 0.08)
    draw.rectangle([sx, sy, sx + 22, sy + 22], fill=(246, 244, 238), outline=INK)
    draw.rectangle([sx + 9, sy + 4, sx + 13, sy + 18], fill=(178, 44, 40))
    draw.rectangle([sx + 4, sy + 9, sx + 18, sy + 13], fill=(178, 44, 40))
    # Three beds: frame, pillow, a patient's head and a blanket body.
    blanket = [(150, 96, 84), (96, 116, 140), (140, 128, 92)]
    for i, fx in enumerate((0.05, 0.35, 0.65)):
        bx = x + int(w * fx)
        bw = int(w * 0.25)
        by = y + int(h * 0.60)
        draw.rectangle([bx, by, bx + bw, by + 5], fill=(120, 118, 112))
        draw.line([bx + 3, by + 5, bx + 3, floor_y + 6], fill=(90, 88, 84), width=2)
        draw.line([bx + bw - 3, by + 5, bx + bw - 3, floor_y + 6],
                  fill=(90, 88, 84), width=2)
        draw.rectangle([bx + 2, by - 6, bx + 13, by], fill=(244, 242, 236))
        draw.ellipse([bx + 4, by - 13, bx + 12, by - 5], fill=(198, 150, 110))
        draw.rectangle([bx + 13, by - 5, bx + bw - 2, by], fill=blanket[i])
    # Two responders in pale protective suits, one at each end.
    for fx, suit in ((0.325, (238, 240, 242)), (0.94, (214, 228, 230))):
        cx = x + int(w * fx)
        top = y + int(h * 0.30)
        draw.ellipse([cx - 8, top, cx + 8, top + 16], fill=suit, outline=(120, 124, 126))
        draw.rectangle([cx - 6, top + 6, cx + 6, top + 11], fill=(96, 130, 150))
        draw.rectangle([cx - 10, top + 16, cx + 10, floor_y + 4], fill=suit)
        draw.line([cx - 10, top + 26, cx + 10, top + 26], fill=(190, 196, 198), width=2)
    # An IV stand beside the middle bed.
    ix = x + int(w * 0.625)
    draw.line([ix, y + int(h * 0.34), ix, floor_y + 2], fill=(100, 100, 100), width=2)
    draw.rectangle([ix - 4, y + int(h * 0.26), ix + 4, y + int(h * 0.36)],
                   fill=(196, 220, 228), outline=(100, 110, 116))
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="br")


def paint_cyclone(draw, x, y, w, h, spec):
    draw.rectangle([x, y, x + w, y + h], fill=(44, 92, 128))
    cx, cy = x + int(w * 0.38), y + int(h * 0.52)
    # Spiral storm bands: arcs of shrinking radius, alternating tones.
    for i, r in enumerate(range(int(h * 0.52), 8, -9)):
        tone = (226, 232, 236) if i % 2 == 0 else (170, 196, 214)
        draw.arc([cx - r, cy - int(r * 0.72), cx + r, cy + int(r * 0.72)],
                 i * 55, i * 55 + 250, fill=tone, width=5)
    draw.ellipse([cx - 6, cy - 5, cx + 6, cy + 5], fill=(30, 60, 92))
    # Irregular island with a palm, lower right.
    ix, iy = x + int(w * 0.70), y + int(h * 0.74)
    draw.polygon([(ix, iy), (ix + 16, iy - 7), (ix + 34, iy - 3), (ix + 46, iy + 3),
                  (ix + 30, iy + 7), (ix + 10, iy + 6)], fill=(74, 130, 74))
    draw.line([ix + 24, iy - 4, ix + 27, iy - 18], fill=(90, 64, 40), width=3)
    for ang in (200, 250, 300, 340):
        ex = ix + 27 + int(11 * math.cos(math.radians(ang)))
        ey = iy - 18 + int(7 * math.sin(math.radians(ang)))
        draw.line([ix + 27, iy - 18, ex, ey], fill=(52, 116, 56), width=2)
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="tr")


def _flag_detail(draw, fx, fy, fw, fh, name, base):
    """A flag rectangle with national detail where the name calls for it."""
    draw.rectangle([fx, fy, fx + fw, fy + fh], fill=base, outline=(20, 20, 20))
    if name == "CHINA":
        draw.rectangle([fx, fy, fx + fw, fy + fh], fill=(196, 32, 36))
        draw.polygon([(fx + 7, fy + 4), (fx + 9, fy + 9), (fx + 12, fy + 9),
                      (fx + 10, fy + 11), (fx + 11, fy + 15), (fx + 7, fy + 12),
                      (fx + 4, fy + 15), (fx + 5, fy + 11), (fx + 2, fy + 9),
                      (fx + 5, fy + 9)], fill=(250, 214, 60))
        for sx, sy in ((16, 4), (19, 8), (19, 13), (15, 16)):
            draw.ellipse([fx + sx - 1, fy + sy - 1, fx + sx + 2, fy + sy + 2],
                         fill=(250, 214, 60))
    elif name == "RUSSIA":
        third = fh // 3
        draw.rectangle([fx, fy, fx + fw, fy + third], fill=(238, 238, 238))
        draw.rectangle([fx, fy + third, fx + fw, fy + 2 * third], fill=(52, 84, 168))
        draw.rectangle([fx, fy + 2 * third, fx + fw, fy + fh], fill=(196, 40, 44))
    elif name == "USA":
        stripe = max(2, fh // 7)
        for i in range(7):
            tone = (178, 44, 52) if i % 2 == 0 else (240, 240, 240)
            draw.rectangle([fx, fy + i * stripe, fx + fw, fy + (i + 1) * stripe], fill=tone)
        draw.rectangle([fx, fy, fx + int(fw * 0.42), fy + 4 * stripe], fill=(52, 56, 110))


def paint_summit(draw, x, y, w, h, spec):
    draw.rectangle([x, y, x + w, y + h], fill=(88, 94, 112))
    draw.rectangle([x, y, x + w, y + int(h * 0.62)], fill=(104, 110, 128))
    flags = spec.get("flags") or [["CHINA", [178, 34, 34]], ["RUSSIA", [52, 84, 160]],
                                  ["USA", [60, 59, 110]]]
    names = ["XI", "PUTIN", "TRUMP"]
    hair = [(18, 18, 18), (168, 168, 168), (232, 190, 90)]
    suits = [(30, 34, 52), (52, 40, 40), (28, 44, 84)]
    skin = (232, 192, 158)
    xs = [x + int(w * f) for f in (0.20, 0.50, 0.80)]
    fw, fh = int(w * 0.17), int(h * 0.26)
    for (fname, rgb), cx in zip(flags, xs):
        _flag_detail(draw, cx - fw // 2, y + int(h * 0.07), fw, fh, fname, tuple(rgb))
        label_chip(draw, cx - fw // 2, y + int(h * 0.07) + fh + 1, fw, 14,
                   fname, size=9, align="tl")
    table_y = y + int(h * 0.70)
    head_top = y + int(h * 0.40)
    for i, cx in enumerate(xs):
        person(draw, cx, head_top, 1.35, skin, hair[i], suits[i])
        # Microphone angled in from the table.
        draw.line([cx + 18, table_y, cx + 7, head_top + 30], fill=(16, 16, 18), width=2)
        draw.ellipse([cx + 4, head_top + 25, cx + 10, head_top + 31], fill=(16, 16, 18))
    # Putin-Trump handshake ABOVE the table edge, against the wall,
    # centred between the two leaders and drawn extra large: the clasp
    # is the hero's central claim and must survive thumbnail scale, so
    # cuffs, sleeves and the clasp itself are chunky.
    hx = (xs[1] + xs[2]) // 2
    hy = table_y - int(h * 0.20)
    draw.line([xs[1] + 16, table_y - 4, hx - 18, hy + 3], fill=suits[1], width=10)
    draw.line([xs[2] - 16, table_y - 4, hx + 18, hy + 3], fill=suits[2], width=10)
    draw.rectangle([hx - 48, hy - 7, hx - 17, hy + 8], fill=(240, 238, 230))
    draw.rectangle([hx + 17, hy - 7, hx + 48, hy + 8], fill=(240, 238, 230))
    draw.ellipse([hx - 20, hy - 13, hx + 20, hy + 15], fill=skin,
                 outline=(150, 110, 78), width=2)
    draw.line([hx - 12, hy - 10, hx + 13, hy + 10], fill=(198, 158, 118), width=4)
    draw.line([hx + 12, hy - 10, hx - 13, hy + 10], fill=(214, 172, 130), width=3)
    draw.line([hx - 3, hy - 12, hx - 3, hy + 12], fill=(198, 158, 118), width=2)
    # The long table and its name plates.
    draw.rectangle([x + int(w * 0.04), table_y, x + int(w * 0.96), y + h], fill=(96, 66, 40))
    draw.rectangle([x + int(w * 0.04), table_y, x + int(w * 0.96), table_y + 4],
                   fill=(140, 104, 62))
    fnt = ImageFont.truetype(SANS_BOLD, 10)
    for name, cx in zip(names, xs):
        pw = width_of(name, fnt) + 12
        draw.rectangle([cx - pw // 2, table_y + 8, cx + pw // 2, table_y + 24],
                       fill=(238, 232, 216))
        draw.text((cx - width_of(name, fnt) // 2, table_y + 11), name,
                  font=fnt, fill=(30, 28, 26))


def paint_case_map(draw, x, y, w, h, spec):
    # Clinic interior: nurse vaccinating a seated child; US poster behind.
    draw.rectangle([x, y, x + w, y + h], fill=(228, 224, 208))
    draw.rectangle([x, y + int(h * 0.78), x + w, y + h], fill=(188, 178, 158))
    # Wall poster with a recognisable US outline and one solid hotspot.
    px, py = x + int(w * 0.58), y + int(h * 0.10)
    pw, ph = int(w * 0.36), int(h * 0.52)
    draw.rectangle([px, py, px + pw, py + ph], fill=(246, 244, 238), outline=INK)
    us = [(0.04, 0.30), (0.14, 0.16), (0.30, 0.10), (0.48, 0.14), (0.62, 0.06),
          (0.78, 0.10), (0.94, 0.22), (0.90, 0.40), (0.80, 0.52), (0.76, 0.72),
          (0.62, 0.80), (0.48, 0.72), (0.34, 0.84), (0.20, 0.70), (0.08, 0.52)]
    draw.polygon([(px + int(a * pw), py + int(b * ph)) for a, b in us],
                 fill=(196, 205, 190), outline=(90, 100, 88))
    hx, hy = px + int(pw * 0.55), py + int(ph * 0.45)
    draw.ellipse([hx - 5, hy - 5, hx + 5, hy + 5], fill=(200, 40, 36))
    fnt = ImageFont.truetype(SANS_BOLD, 8)
    draw.text((px + 4, py + 3), "UNITED STATES", font=fnt, fill=INK)
    # Nurse (teal scrubs, cap) leaning in with a syringe.
    nx = x + int(w * 0.30)
    person(draw, nx, y + int(h * 0.18), 1.3, (232, 192, 158), (240, 240, 240),
           (38, 140, 140), tie=(38, 140, 140))
    draw.line([nx + 14, y + int(h * 0.52), nx + 34, y + int(h * 0.46)],
              fill=(232, 192, 158), width=5)
    draw.line([nx + 34, y + int(h * 0.46), nx + 42, y + int(h * 0.42)],
              fill=(120, 120, 120), width=2)
    # Child on a chair, sleeve up.
    cx2 = x + int(w * 0.47)
    draw.rectangle([cx2 - 12, y + int(h * 0.62), cx2 + 14, y + int(h * 0.80)],
                   fill=(150, 90, 60))
    person(draw, cx2, y + int(h * 0.34), 0.95, (198, 150, 110), (30, 26, 22),
           (70, 110, 190), tie=(70, 110, 190))
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="tl")


def paint_chart_down(draw, x, y, w, h, spec):
    # Trading floor: a big falling board, a labelled 200-day line, traders.
    draw.rectangle([x, y, x + w, y + h], fill=(30, 34, 44))
    bx, by = x + int(w * 0.06), y + int(h * 0.08)
    bw, bh = int(w * 0.88), int(h * 0.52)
    draw.rectangle([bx, by, bx + bw, by + bh], fill=(16, 20, 28), outline=(120, 130, 140))
    pts = [(bx + int(bw * f), by + int(bh * g)) for f, g in
           ((0.02, 0.18), (0.20, 0.26), (0.38, 0.20), (0.55, 0.42),
            (0.72, 0.55), (0.88, 0.78), (0.98, 0.88))]
    draw.line(pts, fill=(240, 80, 60), width=3)
    ref_y = by + int(bh * 0.62)
    for sx in range(bx + 4, bx + bw - 4, 10):
        draw.line([sx, ref_y, sx + 5, ref_y], fill=(240, 200, 80), width=2)
    fnt = ImageFont.truetype(SANS_BOLD, 8)
    draw.text((bx + bw - width_of("200-DAY", fnt) - 4, ref_y - 11), "200-DAY",
              font=fnt, fill=(240, 200, 80))
    draw.polygon([(bx + bw - 8, by + int(bh * 0.88)), (bx + bw - 1, by + int(bh * 0.88)),
                  (bx + bw - 4, by + int(bh * 0.97))], fill=(240, 80, 60))
    # Three traders below the board; the middle one points up at it.
    floor_y = y + int(h * 0.66)
    for i, fx in enumerate((0.22, 0.50, 0.76)):
        cx = x + int(w * fx)
        person(draw, cx, floor_y, 1.05, (232, 192, 158), (36, 30, 26),
               (52, 58, 74), tie=(170, 40, 40))
    mid = x + int(w * 0.50)
    draw.line([mid + 12, floor_y + 16, mid + 26, floor_y - 8], fill=(232, 192, 158), width=4)
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="tl")


def paint_chip(draw, x, y, w, h, spec):
    # Clean-room fab: dark room, glowing wafer, worker in a bunny suit.
    draw.rectangle([x, y, x + w, y + h], fill=(36, 44, 56))
    for gx in range(x + 8, x + w, 26):
        draw.line([gx, y + 4, gx, y + int(h * 0.30)], fill=(70, 84, 100), width=2)
    # Glowing wafer on its pedestal, left.
    wx, wy = x + int(w * 0.28), y + int(h * 0.52)
    draw.ellipse([wx - 26, wy - 26, wx + 26, wy + 26], fill=(90, 220, 230))
    draw.ellipse([wx - 18, wy - 18, wx + 18, wy + 18], fill=(160, 245, 250))
    for r in (6, 12):
        draw.ellipse([wx - r, wy - r, wx + r, wy + r], outline=(60, 160, 175))
    draw.rectangle([wx - 4, wy + 26, wx + 4, y + h - 8], fill=(110, 120, 130))
    # Bunny-suited worker beside it, visor and white suit.
    cx = x + int(w * 0.66)
    top = y + int(h * 0.16)
    draw.ellipse([cx - 11, top, cx + 11, top + 22], fill=(238, 240, 242))
    draw.rectangle([cx - 8, top + 7, cx + 8, top + 13], fill=(70, 90, 110))
    draw.rectangle([cx - 14, top + 22, cx + 14, y + h - 6], fill=(232, 234, 236))
    draw.line([cx - 14, top + 34, wx + 24, wy - 6], fill=(232, 234, 236), width=6)
    # A second lit panel on the right wall.
    draw.rectangle([x + int(w * 0.86), y + int(h * 0.20), x + int(w * 0.96),
                    y + int(h * 0.55)], fill=(52, 66, 84), outline=(120, 140, 150))
    rng = Lcg(9)
    for _ in range(6):
        dx = x + int(w * 0.86) + 3 + rng.below(int(w * 0.08))
        dy = y + int(h * 0.20) + 3 + rng.below(int(h * 0.30))
        draw.rectangle([dx, dy, dx + 2, dy + 2], fill=(120, 230, 200))
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="tl")


def paint_missiles(draw, x, y, w, h, spec):
    # Night sky over a skyline: incoming drone trails are BROKEN by
    # interception bursts high above the rooftops - nothing reaches
    # the city, matching the "repel" headline.
    draw.rectangle([x, y, x + w, y + h], fill=(26, 30, 48))
    rng = Lcg(17)
    for _ in range(16):
        sx = x + 3 + rng.below(w - 6)
        sy = y + 3 + rng.below(int(h * 0.5))
        draw.rectangle([sx, sy, sx + 1, sy + 1], fill=(200, 205, 220))
    # City skyline along the bottom, windows lit, rooftops intact.
    ground_y = y + h
    rng2 = Lcg(29)
    bx = x + 2
    while bx < x + w - 14:
        bw = 14 + rng2.below(12)
        bh = int(h * (0.16 + 0.10 * (rng2.below(10) / 10.0)))
        draw.rectangle([bx, ground_y - bh, bx + bw, ground_y], fill=(16, 18, 26))
        for _ in range(3):
            wx = bx + 2 + rng2.below(max(2, bw - 5))
            wy = ground_y - bh + 3 + rng2.below(max(2, bh - 6))
            draw.rectangle([wx, wy, wx + 2, wy + 2], fill=(240, 200, 110))
        bx += bw + 3
    sky_y = y + int(h * 0.52)  # nothing hostile crosses this line
    # Three incoming trails from the top corners, each ending mid-sky
    # in an interception burst, with short debris segments falling
    # away below the burst - and stopping there.
    incomings = [(0.06, 0.30, 0.34), (0.42, 0.62, 0.26), (0.94, 0.72, 0.40)]
    for fx0, fx1, fy1 in incomings:
        x0, y0 = x + int(w * fx0), y + 2
        x1, y1 = x + int(w * fx1), y + int(h * fy1)
        steps = 14
        for t in range(steps):  # broken trail: draw only even segments
            if t % 2 == 1:
                continue
            f0, f1 = t / steps, (t + 1) / steps
            draw.line([x0 + (x1 - x0) * f0, y0 + (y1 - y0) * f0,
                       x0 + (x1 - x0) * f1, y0 + (y1 - y0) * f1],
                      fill=(250, 170, 90), width=2)
        # A rising interceptor streak from the skyline to the same point.
        ix0 = x1 - int(w * 0.10)
        draw.line([ix0, sky_y + int(h * 0.18), x1, y1], fill=(170, 220, 250), width=2)
        # The interception burst itself, well above the rooftops.
        star_burst(draw, x1, y1, max(8, h // 9), (255, 190, 80),
                   seed=int(fx1 * 100) + 5)
        draw.ellipse([x1 - 3, y1 - 3, x1 + 3, y1 + 3], fill=(255, 240, 200))
        # Debris: two short segments tumbling below the burst, fading
        # out long before the skyline.
        for dx, dy, ln in ((-8, 10, 5), (6, 14, 4)):
            draw.line([x1 + dx, y1 + dy, x1 + dx + ln, y1 + dy + 3],
                      fill=(200, 150, 110), width=2)


def paint_probe(draw, x, y, w, h, spec):
    draw.rectangle([x, y, x + w, y + h], fill=(14, 16, 30))
    rng = Lcg(31)
    for _ in range(30):
        sx = x + 2 + rng.below(w - 4)
        sy = y + 2 + rng.below(h - 4)
        s = 1 + rng.below(2)
        draw.rectangle([sx, sy, sx + s, sy + s], fill=(215, 220, 235))
    # Earth, a small blue marble far right.
    ex, ey = x + int(w * 0.86), y + int(h * 0.30)
    draw.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=(70, 130, 220))
    draw.ellipse([ex - 4, ey - 6, ex + 3, ey - 1], fill=(90, 190, 110))
    # The probe: big dish, bus, long booms.
    cx, cy = x + int(w * 0.42), y + int(h * 0.48)
    draw.arc([cx - 30, cy - 26, cx + 6, cy + 26], 270, 90, fill=(225, 228, 232), width=4)
    draw.ellipse([cx - 30, cy - 26, cx + 6, cy + 26], outline=(150, 155, 165))
    draw.rectangle([cx - 2, cy - 8, cx + 16, cy + 8], fill=(190, 160, 90))
    draw.line([cx + 8, cy, cx + 44, cy - 20], fill=(200, 205, 210), width=2)
    draw.line([cx + 8, cy, cx + 48, cy + 12], fill=(200, 205, 210), width=2)
    draw.ellipse([cx + 42, cy - 23, cx + 48, cy - 17], fill=(230, 232, 235))
    draw.line([cx - 12, cy, cx - 30, cy], fill=(230, 232, 235), width=2)
    # Signal arcs travelling toward Earth.
    for r in (12, 20, 28):
        draw.arc([ex - 16 - r, ey - r, ex - 16 + r, ey + r], 300, 60,
                 fill=(140, 200, 250), width=2)
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="bl")


def paint_ballot(draw, x, y, w, h, spec):
    # Parliament chamber: tiered seat rows, raised hands, a rostrum.
    draw.rectangle([x, y, x + w, y + h], fill=(96, 74, 54))
    draw.rectangle([x, y, x + w, y + int(h * 0.30)], fill=(120, 94, 66))
    # Rostrum, centre front.
    rx = x + w // 2
    draw.rectangle([rx - 16, y + int(h * 0.30), rx + 16, y + int(h * 0.52)],
                   fill=(70, 50, 34))
    person(draw, rx, y + int(h * 0.10), 0.9, (232, 192, 158), (40, 36, 32),
           (34, 38, 60), tie=(160, 36, 36))
    # Three rows of seats with heads; many arms raised.
    rng = Lcg(53)
    for row, fy in enumerate((0.58, 0.72, 0.86)):
        ry = y + int(h * fy)
        draw.rectangle([x + 6, ry + 8, x + w - 6, ry + 13], fill=(70, 50, 34))
        for i in range(9):
            hx = x + int(w * (0.08 + 0.105 * i))
            draw.ellipse([hx - 4, ry - 4, hx + 4, ry + 4], fill=(222, 182, 148))
            if rng.below(10) < 6:
                draw.line([hx + 5, ry + 6, hx + 10, ry - 8], fill=(222, 182, 148), width=3)
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="tr")


def paint_scales(draw, x, y, w, h, spec):
    # Courtroom: panelled wall, three judges on a high bench, and a small
    # scales-of-justice standing on the bench front.
    draw.rectangle([x, y, x + w, y + h], fill=(104, 82, 58))
    for px in range(x + 10, x + w - 10, 34):
        draw.rectangle([px, y + 8, px + 26, y + int(h * 0.44)], outline=(70, 54, 36), width=2)
    bench_y = y + int(h * 0.52)
    for fx in (0.26, 0.50, 0.74):
        cx = x + int(w * fx)
        person(draw, cx, y + int(h * 0.20), 1.15, (230, 190, 155), (210, 210, 210),
               (26, 26, 30), tie=(240, 240, 240))
    draw.rectangle([x + 4, bench_y, x + w - 4, y + h - 4], fill=(74, 54, 36))
    draw.rectangle([x + 4, bench_y, x + w - 4, bench_y + 4], fill=(96, 72, 46))
    # Scales: post, beam, two hanging pans, centred on the bench front.
    cx = x + w // 2
    top = bench_y + 12
    draw.line([cx, top, cx, top + 22], fill=(232, 196, 90), width=3)
    draw.line([cx - 20, top + 3, cx + 20, top + 3], fill=(232, 196, 90), width=3)
    for px in (cx - 20, cx + 20):
        draw.line([px, top + 3, px - 6, top + 16], fill=(232, 196, 90), width=1)
        draw.line([px, top + 3, px + 6, top + 16], fill=(232, 196, 90), width=1)
        draw.arc([px - 8, top + 12, px + 8, top + 22], 0, 180, fill=(232, 196, 90), width=2)
    draw.rectangle([cx - 7, top + 22, cx + 7, top + 25], fill=(232, 196, 90))


def paint_tents(draw, x, y, w, h, spec):
    # A flooded camp: grey sky, a row of tents on a ground line, puddles.
    draw.rectangle([x, y, x + w, y + h], fill=(150, 158, 164))
    rng = Lcg(67)
    for _ in range(22):
        rx = x + rng.below(w)
        ry = y + rng.below(int(h * 0.5))
        draw.line([rx, ry, rx - 2, ry + 7], fill=(110, 122, 132), width=1)
    ground_y = y + int(h * 0.80)
    draw.rectangle([x, ground_y, x + w, y + h], fill=(96, 92, 80))
    tones = [(196, 188, 168), (172, 164, 148), (206, 198, 178), (160, 152, 136),
             (188, 180, 160)]
    n = 5
    tw = w // n
    for i in range(n):
        tx = x + i * tw + 4
        apex = ground_y - int(h * 0.42)
        draw.polygon([(tx, ground_y), (tx + tw // 2, apex), (tx + tw - 8, ground_y)],
                     fill=tones[i], outline=(90, 86, 76))
        draw.polygon([(tx + tw // 2 - 6, ground_y), (tx + tw // 2, apex + 12),
                      (tx + tw // 2 + 6, ground_y)], fill=(70, 66, 58))
    # Flood puddles in front of the tents.
    for i in range(4):
        px = x + int(w * (0.10 + 0.24 * i))
        draw.ellipse([px, ground_y + 5, px + 30, ground_y + 11], fill=(140, 165, 180))


def paint_conference(draw, x, y, w, h, spec):
    # Climate-conference chamber: panelled wall, a backdrop banner,
    # five delegates seated at one long table with small flags.
    draw.rectangle([x, y, x + w, y + h], fill=(208, 202, 188))
    draw.rectangle([x + int(w * 0.30), y + int(h * 0.08), x + int(w * 0.70),
                    y + int(h * 0.34)], fill=(70, 96, 84))
    fnt = ImageFont.truetype(SANS_BOLD, 11)
    draw.text((x + w // 2 - width_of("COP31", fnt) // 2, y + int(h * 0.16)),
              "COP31", font=fnt, fill=(240, 238, 228))
    table_y = y + int(h * 0.68)
    skin = (232, 192, 158)
    suits = [(52, 58, 74), (84, 60, 52), (44, 66, 58), (66, 52, 76), (58, 62, 50)]
    hair = [(30, 28, 26), (120, 90, 60), (18, 18, 18), (200, 200, 200), (60, 44, 30)]
    for i, fx in enumerate((0.14, 0.32, 0.50, 0.68, 0.86)):
        cx = x + int(w * fx)
        person(draw, cx, y + int(h * 0.36), 1.05, skin, hair[i], suits[i],
               tie=(240, 238, 230))
        # A small table flag in front of each delegate.
        draw.line([cx + 10, table_y, cx + 10, table_y - 12], fill=(60, 58, 54), width=1)
        draw.rectangle([cx + 10, table_y - 12, cx + 18, table_y - 7],
                       fill=(168, 60, 50) if i % 2 == 0 else (60, 90, 150))
    draw.rectangle([x + int(w * 0.03), table_y, x + int(w * 0.97), y + h - 3],
                   fill=(110, 84, 56))
    draw.rectangle([x + int(w * 0.03), table_y, x + int(w * 0.97), table_y + 4],
                   fill=(146, 112, 72))
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="tl")


def paint_gta_skyline(draw, x, y, w, h, spec):
    # Muted dusk over a coastal game city: dusty purple-to-apricot sky,
    # a low sun, dark skyline silhouettes, palms, lit windows, water.
    # Saturation deliberately kept low - dusk, never neon.
    draw.rectangle([x, y, x + w, y + int(h * 0.30)], fill=(94, 82, 108))
    draw.rectangle([x, y + int(h * 0.30), x + w, y + int(h * 0.55)], fill=(146, 104, 102))
    draw.rectangle([x, y + int(h * 0.55), x + w, y + int(h * 0.78)], fill=(198, 132, 84))
    sea_y = y + int(h * 0.78)
    draw.rectangle([x, sea_y, x + w, y + h], fill=(56, 58, 88))
    sun_r = max(7, h // 7)
    sun_cx, sun_cy = x + int(w * 0.34), sea_y - 2
    draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
                 fill=(236, 186, 116))
    draw.rectangle([x, sea_y - 2, x + w, sea_y], fill=(120, 84, 84))
    # Skyline: two dark rows of towers with sparse amber windows.
    rng = Lcg(97)
    for base_f, tone, hmin, hmax in ((0.78, (70, 62, 84), 0.18, 0.38),
                                     (0.80, (40, 38, 52), 0.28, 0.58)):
        bx = x + 1
        base = y + int(h * base_f)
        while bx < x + w - 10:
            bw = 9 + rng.below(10)
            bh = int(h * (hmin + (hmax - hmin) * (rng.below(10) / 10.0)))
            draw.rectangle([bx, base - bh, bx + bw, base], fill=tone)
            for _ in range(3):
                if rng.below(10) < 5:
                    wx = bx + 2 + rng.below(max(2, bw - 4))
                    wy = base - bh + 3 + rng.below(max(2, bh - 6))
                    draw.rectangle([wx, wy, wx + 2, wy + 2], fill=(238, 198, 120))
            bx += bw + 2 + rng.below(4)
    # Palm silhouettes in the foreground.
    for fx in (0.08, 0.90):
        px, py = x + int(w * fx), y + h
        draw.line([px, py, px + 3, py - int(h * 0.34)], fill=(24, 24, 30), width=3)
        for ang in (160, 200, 250, 300, 345):
            ex = px + 3 + int(13 * math.cos(math.radians(ang)))
            ey = py - int(h * 0.34) + int(8 * math.sin(math.radians(ang)))
            draw.line([px + 3, py - int(h * 0.34), ex, ey], fill=(24, 24, 30), width=2)
    # Sun glitter on the water.
    for i in range(5):
        gy = sea_y + 3 + i * 3
        gw = 16 - 2 * i
        draw.line([sun_cx - gw // 2, gy, sun_cx + gw // 2, gy],
                  fill=(214, 160, 96), width=1)
    label_chip(draw, x, y, w, h, spec.get("label", ""), align="tl")


# Dotted world map: rows of land cells over a 52x20 grid (stylised -
# continents readable, coastlines approximate).
MAP_ROWS = [
    "                                                    ",
    "     ##### ##           ##################          ",
    "    ###########        #####################        ",
    "   #############       #######################      ",
    "    ##########          #####################       ",
    "     ########            ######## ##########        ",
    "      ######              ######   ########         ",
    "       ####               #######   ######          ",
    "       ###                ########   ####           ",
    "      ####                ########  ######          ",
    "     ######               #######  #########        ",
    "     ######                #####   #########        ",
    "      ####                  ###     ########        ",
    "      ###                   ##       ######         ",
    "       ##                                            ",
    "       #                                             ",
    "                                                    ",
    "                                                    ",
    "                                                    ",
    "                                                    ",
]

# Region -> (fx, fy) anchor on the map, aligned to MAP_ROWS landmass.
REGION_ANCHORS = {
    "North America": (0.17, 0.24),
    "South America": (0.14, 0.60),
    "Europe": (0.50, 0.16),
    "Africa": (0.56, 0.50),
    "Middle East": (0.615, 0.30),
    "Asia": (0.76, 0.20),
    "Oceania": (0.85, 0.60),
}


def _map_jitter(k):
    """Deterministic small offset for the k-th item in one region."""
    return ((k % 3) - 1) * 0.045, (((k // 3) % 3) - 1) * 0.075


def paint_worldmap(draw, x, y, w, h, spec):
    """Dotted landmass with numbered pins (illustrated stories) and
    plain dots (briefs), placed by each story's region. spec carries
    'pins': [(num, region)] and 'dots': [region]."""
    cols = len(MAP_ROWS[0])
    rows = len(MAP_ROWS)
    for r, row in enumerate(MAP_ROWS):
        for c, cell in enumerate(row):
            if cell == "#":
                cx = x + int((c + 0.5) * w / cols)
                cy = y + int((r + 0.5) * h / rows)
                draw.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(168, 162, 148))
    seen_pins, seen_dots = {}, {}

    def _place(region, seen, phase=0):
        k = seen.get(region, 0)
        seen[region] = k + 1
        ax, ay = REGION_ANCHORS[region]
        jx, jy = _map_jitter(k + phase)
        return x + int((ax + jx) * w), y + int((ay + jy) * h)

    for region in spec.get("dots") or []:
        cx, cy = _place(region, seen_dots, phase=1)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(96, 92, 86))
    fnt = ImageFont.truetype(SANS_BOLD, 7)
    for num, region in spec.get("pins") or []:
        cx, cy = _place(region, seen_pins)
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(168, 38, 32),
                     outline=(247, 243, 234))
        label = str(num)
        draw.text((cx - width_of(label, fnt) // 2, cy - 4), label,
                  font=fnt, fill=(247, 243, 234))


PAINTERS = {
    "sea_strike": paint_sea_strike,
    "bridge_fallen": paint_bridge_fallen,
    "clinic_ward": paint_clinic_ward,
    "cyclone": paint_cyclone,
    "summit": paint_summit,
    "case_map": paint_case_map,
    "chart_down": paint_chart_down,
    "chip": paint_chip,
    "missiles": paint_missiles,
    "probe": paint_probe,
    "ballot": paint_ballot,
    "scales": paint_scales,
    "tents": paint_tents,
    "conference": paint_conference,
    "gta_skyline": paint_gta_skyline,
    "worldmap": paint_worldmap,
}
