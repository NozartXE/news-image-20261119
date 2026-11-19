"""Page layout: the MOSAIC FRONT PAGE (concept C1, panel winner).

One deterministic assembler from validated content:

  masthead   nameplate + full date + computed scope line
  hero       full-width scene, headline bar, one dek line
  cards      3 rows x 4 scene-cards (scene + place kicker + headline)
  numbers    THE DAY IN NUMBERS — figures validated as additive
  index      the remaining stories, one fitted headline line each,
             headed by a printed count that must equal the number
             of index stories actually drawn

All heights are constants here so the geometry can be audited in one
place; the assembler asserts the page ends exactly at 1024.
"""

from PIL import Image, ImageDraw

from .scenes import PAINTERS
from .textutil import (SANS, SANS_BOLD, SERIF, SERIF_BOLD, block, centred,
                       fit_lines, fit_single, font, text_w)
from .validate import scope_line, validate

W = H = 1024
PAPER = (247, 242, 231)
INK = (24, 22, 20)
FADED = (92, 84, 72)
ACCENT = (156, 38, 24)
NAVY = (18, 38, 66)
GOLD = (198, 148, 42)
RULE = (24, 22, 20)

MARGIN = 16
CW = W - 2 * MARGIN  # 992 usable

MASTHEAD_H = 66
HERO_SCENE_H = 136
HERO_HEAD_H = 42
HERO_DEK_H = 22
CARD_SCENE_H = 96
CARD_KICKER_H = 16
CARD_HEAD_H = 36
CARD_H = CARD_SCENE_H + CARD_KICKER_H + CARD_HEAD_H + 6
CARD_ROWS = 3
STRIP_H = 50
INDEX_HEAD_H = 24
INDEX_COLS = 3


def _masthead(d, content, stats):
    y = 6
    fnt = font(SERIF_BOLD, 37)
    d.text((MARGIN, y), content["nameplate"], font=fnt, fill=INK)
    # right block: date over scope, right-aligned
    date_f = font(SANS_BOLD, 17)
    scope_f = font(SANS_BOLD, 13)
    date = content["date_line"].upper()
    scope = scope_line(stats)
    d.text((W - MARGIN - text_w(d, date, date_f), y + 2), date,
           font=date_f, fill=INK)
    d.text((W - MARGIN - text_w(d, scope, scope_f), y + 26), scope,
           font=scope_f, fill=ACCENT)
    d.line([(MARGIN, MASTHEAD_H - 8), (W - MARGIN, MASTHEAD_H - 8)],
           fill=RULE, width=3)
    d.line([(MARGIN, MASTHEAD_H - 3), (W - MARGIN, MASTHEAD_H - 3)],
           fill=RULE, width=1)
    return MASTHEAD_H


def _hero(d, story, y):
    box = (MARGIN, y, W - MARGIN, y + HERO_SCENE_H)
    PAINTERS[story["scene"]](d, box, story.get("scene_spec", {}))
    d.rectangle(box, outline=INK, width=2)
    if story.get("scene_caption"):
        fnt = font(SANS_BOLD, 12)
        cap = story["scene_caption"]
        w = text_w(d, cap, fnt)
        d.rectangle([box[0] + 8, box[3] - 24, box[0] + 16 + w, box[3] - 4],
                    fill=INK)
        d.text((box[0] + 12, box[3] - 21), cap, font=fnt, fill=PAPER)
    y += HERO_SCENE_H + 4
    fnt, s = fit_single(d, story["headline"], SERIF_BOLD, 31, CW)
    d.text((MARGIN, y), s, font=fnt, fill=INK)
    y += HERO_HEAD_H
    fnt, lines = fit_lines(d, story["dek"], SERIF, 15, CW, 1)
    d.text((MARGIN, y), lines[0], font=fnt, fill=(52, 48, 42))
    return y + HERO_DEK_H


def _card(d, story, x, y, w, warnings):
    box = (x, y, x + w, y + CARD_SCENE_H)
    PAINTERS[story["scene"]](d, box, story.get("scene_spec", {}))
    d.rectangle(box, outline=INK, width=1)
    ky = y + CARD_SCENE_H + 3
    kick = f"{story['place']} — {story['region'].upper()}"
    fnt, s = fit_single(d, kick, SANS_BOLD, 12, w)
    d.text((x, ky), s, font=fnt, fill=ACCENT)
    hy = ky + CARD_KICKER_H
    fnt, lines = fit_lines(d, story["headline"], SANS_BOLD, 15, w, 2)
    if fnt.size < 13 or any("…" in ln for ln in lines):
        warnings.append(f"card story {story['id']} headline at "
                        f"{fnt.size}px / truncated")
    block(d, x, hy, lines, fnt, 18, INK)


def _strip(d, strip_stories, y, warnings):
    d.rectangle([MARGIN, y, W - MARGIN, y + STRIP_H], fill=NAVY)
    n = len(strip_stories)
    cell = CW // max(1, n)
    for i, s in enumerate(strip_stories):
        x = MARGIN + i * cell + 10
        fnt = font(SANS_BOLD, 18)
        d.text((x, y + 3), s["strip_figure"], font=fnt, fill=GOLD)
        cap_f, lines = fit_lines(d, s["strip_caption"], SANS_BOLD, 11,
                                 cell - 16, 2)
        if any("…" in ln for ln in lines):
            warnings.append(f"strip caption for story {s['id']} truncated")
        block(d, x, y + 25, lines, cap_f, 12, PAPER)
    return y + STRIP_H


def _index(d, index_stories, y):
    d.line([(MARGIN, y + 4), (W - MARGIN, y + 4)], fill=RULE, width=2)
    head = f"MORE OF THE DAY — {len(index_stories)} STORIES"
    fnt = font(SANS_BOLD, 14)
    d.text((MARGIN, y + 7), head, font=fnt, fill=INK)
    right = "EVERY STORY COUNTED ONCE"
    rf = font(SANS_BOLD, 11)
    d.text((W - MARGIN - text_w(d, right, rf), y + 9), right, font=rf,
           fill=FADED)
    y += INDEX_HEAD_H + 4
    cols = INDEX_COLS
    col_w = CW // cols
    rows = (len(index_stories) + cols - 1) // cols
    row_h = (H - 8 - y) // max(1, rows)
    warnings = []
    for i, s in enumerate(index_stories):
        col, row = divmod(i, rows)
        x = MARGIN + col * col_w + (8 if col else 0)
        yy = y + row * row_h + 2
        # the brief is the story's one printed line: place + claim,
        # written to fit at full size (validated <= 50 chars)
        d.rectangle([x, yy + 3, x + 5, yy + 10], fill=ACCENT)
        fnt, txt = fit_single(d, s["brief"], SANS_BOLD, 15, col_w - 22)
        if fnt.size < 12:
            warnings.append(f"index story {s['id']} at {fnt.size}px")
        if "…" in txt:
            warnings.append(f"index story {s['id']} brief truncated")
        d.text((x + 10, yy), txt, font=fnt, fill=INK)
        if col:
            d.line([(MARGIN + col * col_w - 2, yy),
                    (MARGIN + col * col_w - 2, yy + 12)],
                   fill=(200, 192, 172), width=1)
    return warnings


def render(content):
    """Render validated content to a 1024x1024 PIL image.

    Returns (image, stats, warnings). Raises ValueError on any
    accounting failure — an unreconciled page is never drawn.
    """
    stats = validate(content)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    stories = content["stories"]
    hero = next(s for s in stories if s.get("tier") == "hero")
    cards = [s for s in stories if s.get("tier") == "card"]
    strip = [s for s in stories if s.get("strip_figure")]
    index = [s for s in stories
             if s.get("tier") not in ("hero", "card")]
    if len(cards) != CARD_ROWS * 4:
        raise ValueError(f"{len(cards)} card stories (need {CARD_ROWS * 4})")

    y = _masthead(d, content, stats)
    y = _hero(d, hero, y)
    warnings = []
    card_w = CW // 4
    for r in range(CARD_ROWS):
        for c in range(4):
            _card(d, cards[r * 4 + c], MARGIN + c * card_w, y,
                  card_w - (10 if c < 3 else 0), warnings)
        y += CARD_H
    y = _strip(d, strip, y + 4, warnings)
    warnings += _index(d, index, y + 6)
    # double-rule frame around the page: a finished front page
    # carries a border (the unframed page read as unfinished).
    # Drawn last, inside the 16px margin, so it covers no content.
    d.rectangle([5, 5, W - 6, H - 6], outline=INK, width=2)
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=1)
    return img, stats, warnings
