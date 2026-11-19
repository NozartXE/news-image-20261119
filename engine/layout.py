"""The C1 mosaic assembler.

Canvas 1024x1024, off-white paper, near-black ink, one muted red
accent. The vertical budget is fixed by named constants and sums to
the full canvas height:

    masthead 66 + hero 204 + 3 card rows x 164 + strip 50
    + index head 24 + index rows (the remainder)
"""

from PIL import Image, ImageDraw

from . import textutil as tu
from .scenes import PAINTERS
from .validate import scope_line

CANVAS = 1024
MARGIN = 16
CONTENT_W = CANVAS - 2 * MARGIN  # 992
GUTTER = 10

MASTHEAD_H = 66
HERO_SCENE_H = 140
HERO_HEADLINE_H = 42
HERO_DEK_H = 22
HERO_H = HERO_SCENE_H + HERO_HEADLINE_H + HERO_DEK_H  # 204

CARD_ROWS = 3
CARD_COLS = 4
CARD_ROW_H = 164
CARD_SCENE_H = 96
CARD_KICKER_H = 16

STRIP_H = 50
INDEX_HEAD_H = 24

PAPER = (247, 243, 234)
INK = (26, 24, 22)
ACCENT = (168, 38, 32)
GREY = (96, 92, 86)
HAIRLINE = (40, 38, 34)
STRIP_BG = (24, 30, 46)
STRIP_FIG = (244, 196, 84)


def _text(draw, xy, text, fnt, fill=INK):
    draw.text(xy, text, font=fnt, fill=fill)


def _fit_headline(draw, text, width, sizes=(15, 14, 13)):
    """Wrap a card headline to at most two lines, shrinking if needed."""
    for size in sizes:
        fnt = tu.font(tu.SANS_BOLD, size)
        lines = tu.wrap(text, fnt, width)
        if len(lines) <= 2:
            return fnt, lines
    return fnt, lines[:2]


def _caption_chip(draw, x, y, text):
    fnt = tu.font(tu.SANS_BOLD, 11)
    tw = tu.width_of(text, fnt)
    draw.rectangle([x, y, x + tw + 12, y + 17], fill=(18, 18, 20))
    _text(draw, (x + 6, y + 3), text, fnt, fill=(245, 242, 235))


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

    y = 0
    # ---- masthead ------------------------------------------------------
    name_fnt = tu.font(tu.SERIF_BOLD, 36)
    _text(draw, (MARGIN, y + 12), content["nameplate"], name_fnt)
    date_fnt = tu.font(tu.SANS_BOLD, 15)
    date = content["date_line"].upper()
    _text(draw, (CANVAS - MARGIN - tu.width_of(date, date_fnt), y + 10),
          date, date_fnt)
    scope_fnt = tu.font(tu.SANS_BOLD, 13)
    scope = scope_line(stats)
    _text(draw, (CANVAS - MARGIN - tu.width_of(scope, scope_fnt), y + 32),
          scope, scope_fnt, fill=ACCENT)
    draw.rectangle([MARGIN, y + MASTHEAD_H - 6, CANVAS - MARGIN, y + MASTHEAD_H - 3],
                   fill=INK)
    y += MASTHEAD_H

    # ---- hero band -----------------------------------------------------
    PAINTERS[hero["scene"]](draw, MARGIN, y, CONTENT_W, HERO_SCENE_H,
                            hero.get("scene_spec") or {})
    draw.rectangle([MARGIN, y, MARGIN + CONTENT_W, y + HERO_SCENE_H],
                   outline=HAIRLINE)
    if hero.get("scene_caption"):
        _caption_chip(draw, MARGIN + 6, y + HERO_SCENE_H - 23,
                      hero["scene_caption"])
    y += HERO_SCENE_H
    hfnt, _hsize, _ = tu.fit_to_width(hero["headline"], tu.SERIF_BOLD, 31,
                                      CONTENT_W, 18)
    _text(draw, (MARGIN, y + 5), hero["headline"], hfnt)
    y += HERO_HEADLINE_H
    dfnt, _dsize, _ = tu.fit_to_width(hero["dek"], tu.SANS, 14, CONTENT_W, 11)
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
            kicker = "%s — %s" % (story["place"], story["region"].upper())
            kfnt, _ks, _ = tu.fit_to_width(kicker, tu.SANS_BOLD, 11, cw, 9)
            _text(draw, (cx, y + CARD_SCENE_H + 3), kicker, kfnt, fill=ACCENT)
            hfnt2, lines = _fit_headline(draw, story["headline"], cw)
            ly = y + CARD_SCENE_H + CARD_KICKER_H + 2
            for line in lines:
                _text(draw, (cx, ly), line, hfnt2)
                ly += 18
        y += CARD_ROW_H

    # ---- numbers strip ---------------------------------------------------
    draw.rectangle([MARGIN, y, MARGIN + CONTENT_W, y + STRIP_H], fill=STRIP_BG)
    col_w = CONTENT_W // len(strip)
    fig_fnt = tu.font(tu.SANS_BOLD, 19)
    cap_fnt = tu.font(tu.SANS, 11)
    for i, story in enumerate(strip):
        sx = MARGIN + i * col_w + 6
        sw = col_w - 10
        _text(draw, (sx, y + 3), story["strip_figure"], fig_fnt, fill=STRIP_FIG)
        cap_lines = tu.wrap(story["strip_caption"], cap_fnt, sw)[:2]
        cy = y + 26
        for line in cap_lines:
            _text(draw, (sx, cy), line, cap_fnt, fill=(238, 236, 230))
            cy += 12
    y += STRIP_H

    # ---- index -----------------------------------------------------------
    head_fnt = tu.font(tu.SANS_BOLD, 13)
    _text(draw, (MARGIN, y + 3),
          "MORE OF THE DAY — %d STORIES" % len(index), head_fnt)
    note = "EVERY STORY COUNTED ONCE"
    note_fnt = tu.font(tu.SANS, 10)
    _text(draw, (CANVAS - MARGIN - tu.width_of(note, note_fnt), y + 5),
          note, note_fnt, fill=GREY)
    draw.line([MARGIN, y + INDEX_HEAD_H - 2, CANVAS - MARGIN, y + INDEX_HEAD_H - 2],
              fill=INK, width=1)
    y += INDEX_HEAD_H

    rows = (len(index) + 2) // 3
    row_h = (CANVAS - y - 4) // rows
    col_w2 = (CONTENT_W - 2 * GUTTER) // 3
    bullet_fnt = tu.font(tu.SANS_BOLD, 12)
    for pos, story in enumerate(index):
        col, row = divmod(pos, rows)
        ix = MARGIN + col * (col_w2 + GUTTER)
        iy = y + row * row_h + 2
        cw2 = col_w2 if col < 2 else CONTENT_W - 2 * (col_w2 + GUTTER)
        draw.rectangle([ix, iy + 3, ix + 6, iy + 9], fill=ACCENT)
        brief = story["brief"]
        bfnt, bsize, fits = tu.fit_to_width(brief, tu.SANS_BOLD, 15,
                                            cw2 - 12, 12)
        if not fits or bsize < 12:
            warnings.append(
                "story %s brief %r needs %dpx / ellipsis at index width"
                % (story["id"], brief, bsize))
        _text(draw, (ix + 11, iy), brief, bfnt)

    return img, warnings
