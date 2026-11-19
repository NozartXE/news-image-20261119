"""The C1 mosaic assembler.

Canvas 1024x1024, off-white paper, near-black ink, one muted red
accent. The vertical budget is fixed by named constants and sums to
the full canvas height:

    masthead 52 + region bar 18 + hero 208 + 3 card rows x 152
    + strip 42 + index head 22 + index body 190 (15 rows x 12)
    + date check 22 + sources 14 = 1024 (plus slack)

Every illustrated card carries a two-line dek with a figure and a
named source; cards and briefs are numbered continuously 1..43; the
region bar and the dotted pin map are computed from the content, so
the printed counts can be re-derived from the page itself.
"""

from PIL import Image, ImageDraw

from . import textutil as tu
from .scenes import PAINTERS
from .validate import REGION_ORDER, numbering, region_counts, scope_line

CANVAS = 1024
MARGIN = 16
CONTENT_W = CANVAS - 2 * MARGIN  # 992
GUTTER = 10

MASTHEAD_H = 52
REGION_BAR_H = 18
HERO_SCENE_H = 152
HERO_HEADLINE_H = 36
HERO_DEK_H = 20
HERO_H = HERO_SCENE_H + HERO_HEADLINE_H + HERO_DEK_H  # 208

CARD_ROWS = 3
CARD_COLS = 4
CARD_ROW_H = 152
CARD_SCENE_H = 84
CARD_KICKER_H = 13

STRIP_H = 42
INDEX_HEAD_H = 22
MAP_W = 252
DATECHECK_H = 22
SOURCES_H = 14

PAPER = (247, 243, 234)
INK = (26, 24, 22)
ACCENT = (168, 38, 32)
GREY = (96, 92, 86)
DEK_INK = (62, 59, 54)
HAIRLINE = (40, 38, 34)
STRIP_BG = (24, 30, 46)
STRIP_FIG = (244, 196, 84)

# Static furniture, never content-JSON stories, so the 43-story
# reconciliation is untouched. The DATE CHECK box is the only place
# on the page where prior-day figures may be printed.
DATE_CHECK = ("DATE CHECK — NOT TODAY: Nvidia's $115.8bn quarter (17 Nov) · "
              "Dow −561 (18 Nov) · Jeffries Speaker vote 251–11 (18 Nov) · "
              "the Shenzhen handshake (18 Nov, background to today's talks)")


def _text(draw, xy, text, fnt, fill=INK):
    draw.text(xy, text, font=fnt, fill=fill)


def _fit_headline(draw, text, width, sizes=(14, 13, 12)):
    """Wrap a card headline to at most two lines, shrinking if needed."""
    for size in sizes:
        fnt = tu.font(tu.SANS_BOLD, size)
        lines = tu.wrap(text, fnt, width)
        if len(lines) <= 2:
            return fnt, lines
    return fnt, lines[:2]


def _fit_dek(text, width, sizes=(10, 9)):
    """Wrap a card dek to at most two lines, shrinking if needed."""
    for size in sizes:
        fnt = tu.font(tu.SANS, size)
        lines = tu.wrap(text, fnt, width)
        if len(lines) <= 2:
            return fnt, lines
    return fnt, lines[:2]


def _caption_chip(draw, x, y, text):
    fnt = tu.font(tu.SANS_BOLD, 11)
    tw = tu.width_of(text, fnt)
    draw.rectangle([x, y, x + tw + 12, y + 17], fill=(18, 18, 20))
    _text(draw, (x + 6, y + 3), text, fnt, fill=(245, 242, 235))


def _number_badge(draw, x, y, num, size=9, height=13):
    fnt = tu.font(tu.SANS_BOLD, size)
    label = str(num)
    bw = max(15, tu.width_of(label, fnt) + 6)
    draw.rectangle([x, y, x + bw, y + height], fill=INK)
    _text(draw, (x + (bw - tu.width_of(label, fnt)) // 2, y + 2), label,
          fnt, fill=PAPER)
    return bw


def render(content, stats):
    """Draw the whole page. Returns (PIL image, legibility warnings)."""
    warnings = []
    img = Image.new("RGB", (CANVAS, CANVAS), PAPER)
    draw = ImageDraw.Draw(img)
    stories = content["stories"]
    hero = next(s for s in stories if s["tier"] == "hero")
    cards = [s for s in stories if s["tier"] == "card"]
    index = [s for s in stories if s["tier"] not in ("hero", "card")]
    strip = [s for s in stories if s.get("strip_figure")]
    nums = numbering(stories)

    y = 0
    # ---- masthead ------------------------------------------------------
    name_fnt = tu.font(tu.SERIF_BOLD, 29)
    _text(draw, (MARGIN, y + 9), content["nameplate"], name_fnt)
    date_fnt = tu.font(tu.SANS_BOLD, 13)
    date = content["date_line"].upper()
    _text(draw, (CANVAS - MARGIN - tu.width_of(date, date_fnt), y + 8),
          date, date_fnt)
    scope_fnt = tu.font(tu.SANS_BOLD, 11)
    scope = scope_line(stats)
    _text(draw, (CANVAS - MARGIN - tu.width_of(scope, scope_fnt), y + 27),
          scope, scope_fnt, fill=ACCENT)
    draw.rectangle([MARGIN, y + MASTHEAD_H - 5, CANVAS - MARGIN, y + MASTHEAD_H - 2],
                   fill=INK)
    y += MASTHEAD_H

    # ---- region bar: counts computed from the content, summing to 43 ---
    counts = region_counts(stories)
    bar = " · ".join("%s %d" % (region.upper(), counts[region])
                     for region in REGION_ORDER if counts[region])
    bar_fnt = tu.font(tu.SANS_BOLD, 11)
    _text(draw, (MARGIN, y + 3), bar, bar_fnt)
    draw.line([MARGIN, y + REGION_BAR_H - 1, CANVAS - MARGIN, y + REGION_BAR_H - 1],
              fill=HAIRLINE, width=1)
    y += REGION_BAR_H

    # ---- hero band -----------------------------------------------------
    PAINTERS[hero["scene"]](draw, MARGIN, y, CONTENT_W, HERO_SCENE_H,
                            hero.get("scene_spec") or {})
    draw.rectangle([MARGIN, y, MARGIN + CONTENT_W, y + HERO_SCENE_H],
                   outline=HAIRLINE)
    _number_badge(draw, MARGIN + 5, y + 5, nums[hero["id"]])
    if hero.get("scene_caption"):
        _caption_chip(draw, MARGIN + 6, y + HERO_SCENE_H - 23,
                      hero["scene_caption"])
    y += HERO_SCENE_H
    hfnt, _hsize, _ = tu.fit_to_width(hero["headline"], tu.SERIF_BOLD, 28,
                                      CONTENT_W, 18)
    _text(draw, (MARGIN, y + 4), hero["headline"], hfnt)
    y += HERO_HEADLINE_H
    dfnt, _dsize, _ = tu.fit_to_width(hero["dek"], tu.SANS, 13, CONTENT_W, 11)
    _text(draw, (MARGIN, y + 2), hero["dek"], dfnt)
    y += HERO_DEK_H

    # ---- card rows -----------------------------------------------------
    cell_w = (CONTENT_W - (CARD_COLS - 1) * GUTTER) // CARD_COLS
    for row in range(CARD_ROWS):
        for col in range(CARD_COLS):
            story = cards[row * CARD_COLS + col]
            cx = MARGIN + col * (cell_w + GUTTER)
            cw = cell_w if col < CARD_COLS - 1 else CONTENT_W - col * (cell_w + GUTTER)
            PAINTERS[story["scene"]](draw, cx, y, cw, CARD_SCENE_H,
                                     story.get("scene_spec") or {})
            draw.rectangle([cx, y, cx + cw, y + CARD_SCENE_H], outline=HAIRLINE)
            # The number badge sits in the card header (kicker row), so
            # it never collides with a scene's own label chip.
            bw = _number_badge(draw, cx, y + CARD_SCENE_H + 2,
                               nums[story["id"]], size=8, height=11)
            kicker = "%s — %s" % (story["place"], story["region"].upper())
            kfnt, _ks, _ = tu.fit_to_width(kicker, tu.SANS_BOLD, 10,
                                           cw - bw - 5, 8)
            _text(draw, (cx + bw + 5, y + CARD_SCENE_H + 2), kicker, kfnt,
                  fill=ACCENT)
            hfnt2, lines = _fit_headline(draw, story["headline"], cw)
            ly = y + CARD_SCENE_H + CARD_KICKER_H + 2
            for line in lines:
                _text(draw, (cx, ly), line, hfnt2)
                ly += 14
            dfnt2, dlines = _fit_dek(story["dek"], cw)
            dy = y + CARD_SCENE_H + CARD_KICKER_H + 30
            for line in dlines:
                _text(draw, (cx, dy), line, dfnt2, fill=DEK_INK)
                dy += 11
        y += CARD_ROW_H

    # ---- numbers strip: every figure anchored in its story's dek -------
    draw.rectangle([MARGIN, y, MARGIN + CONTENT_W, y + STRIP_H], fill=STRIP_BG)
    col_w = CONTENT_W // len(strip)
    fig_fnt = tu.font(tu.SANS_BOLD, 16)
    cap_fnt = tu.font(tu.SANS, 10)
    for i, story in enumerate(strip):
        sx = MARGIN + i * col_w + 6
        sw = col_w - 10
        _text(draw, (sx, y + 3), story["strip_figure"], fig_fnt, fill=STRIP_FIG)
        cap = tu.ellipsise(story["strip_caption"], cap_fnt, sw)
        if cap != story["strip_caption"]:
            warnings.append("story %s strip caption %r ellipsised at strip width"
                            % (story["id"], story["strip_caption"]))
        _text(draw, (sx, y + 25), cap, cap_fnt, fill=(238, 236, 230))
    y += STRIP_H

    # ---- index head ------------------------------------------------------
    head_fnt = tu.font(tu.SANS_BOLD, 12)
    _text(draw, (MARGIN, y + 4),
          "MORE OF THE DAY — %d STORIES" % len(index), head_fnt)
    note = "EVERY STORY COUNTED ONCE · PINS = ILLUSTRATED, DOTS = BRIEFS"
    note_fnt = tu.font(tu.SANS, 10)
    _text(draw, (CANVAS - MARGIN - tu.width_of(note, note_fnt), y + 5),
          note, note_fnt, fill=GREY)
    draw.line([MARGIN, y + INDEX_HEAD_H - 2, CANVAS - MARGIN, y + INDEX_HEAD_H - 2],
              fill=INK, width=1)
    y += INDEX_HEAD_H

    # ---- index body: pin map column + two numbered brief columns --------
    body_bottom = CANVAS - DATECHECK_H - SOURCES_H
    body_h = body_bottom - y
    map_spec = {
        "pins": [(nums[s["id"]], s["region"]) for s in [hero] + cards],
        "dots": [s["region"] for s in index],
    }
    PAINTERS["worldmap"](draw, MARGIN, y, MAP_W, body_h, map_spec)
    draw.rectangle([MARGIN, y, MARGIN + MAP_W, y + body_h], outline=HAIRLINE)
    map_cap_fnt = tu.font(tu.SANS_BOLD, 9)
    _text(draw, (MARGIN + 5, y + body_h - 14), "WHERE THE DAY HAPPENED",
          map_cap_fnt, fill=GREY)

    rows = (len(index) + 1) // 2
    row_h = body_h // rows
    idx_x = MARGIN + MAP_W + GUTTER
    idx_w = CONTENT_W - MAP_W - GUTTER
    col_w2 = (idx_w - GUTTER) // 2
    for pos, story in enumerate(index):
        col, row = divmod(pos, rows)
        ix = idx_x + col * (col_w2 + GUTTER)
        iy = y + row * row_h + 1
        cw2 = col_w2 if col < 1 else idx_w - col_w2 - GUTTER
        num = "%d." % nums[story["id"]]
        nfnt = tu.font(tu.SANS_BOLD, 10)
        _text(draw, (ix, iy), num, nfnt, fill=ACCENT)
        brief = story["brief"]
        bfnt, bsize, fits = tu.fit_to_width(brief, tu.SANS_BOLD, 11,
                                            cw2 - 24, 9)
        if not fits or bsize < 9:
            warnings.append(
                "story %s brief %r needs %dpx / ellipsis at index width"
                % (story["id"], brief, bsize))
        _text(draw, (ix + 24, iy), brief, bfnt)
    y = body_bottom

    # ---- DATE CHECK box: static text, thin red rule only -----------------
    draw.rectangle([MARGIN, y, CANVAS - MARGIN, y + 2], fill=ACCENT)
    draw.rectangle([MARGIN, y, CANVAS - MARGIN, y + DATECHECK_H - 2],
                   outline=HAIRLINE)
    dcfnt, _ds, _ = tu.fit_to_width(DATE_CHECK, tu.SANS, 10, CONTENT_W - 12, 8)
    _text(draw, (MARGIN + 6, y + 6), DATE_CHECK, dcfnt)
    y += DATECHECK_H

    # ---- sources footer ---------------------------------------------------
    sources = []
    for story in stories:
        for src in story.get("sources") or []:
            if src not in sources:
                sources.append(src)
    src_line = "SOURCES: " + " · ".join(sources)
    sfnt, _ss, _ = tu.fit_to_width(src_line, tu.SANS, 9, CONTENT_W, 7)
    _text(draw, (MARGIN, y + 2), src_line, sfnt, fill=GREY)

    return img, warnings
