"""Text and drawing utilities for the news-image engine.

Deterministic helpers only: font loading, measuring, wrapping and
fitting text to a box by shrinking the point size until it fits.
No randomness, no network, no external assets beyond system fonts.
"""

from pathlib import Path

from PIL import ImageFont

FONT_DIR = Path("/usr/share/fonts/truetype")
SERIF_BOLD = str(FONT_DIR / "dejavu" / "DejaVuSerif-Bold.ttf")
SERIF = str(FONT_DIR / "dejavu" / "DejaVuSerif.ttf")
SANS = str(FONT_DIR / "liberation" / "LiberationSans-Regular.ttf")
SANS_BOLD = str(FONT_DIR / "liberation" / "LiberationSans-Bold.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def text_w(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[2] - box[0]


def text_h(fnt):
    box = fnt.getbbox("Ag")
    return box[3] - box[1]


def centred(draw, cx, y, s, fnt, fill):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


def wrap(draw, s, fnt, width):
    """Greedy word wrap measured against real font metrics."""
    lines, cur = [], ""
    for word in s.split():
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, s, path, start_size, width, max_lines, min_size=9):
    """Wrap s at start_size; shrink until it fits max_lines.

    Returns (font, lines). If it still does not fit at min_size, the
    last line is ellipsised so the box never overflows silently.
    """
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        lines = wrap(draw, s, fnt, width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 1
    fnt = font(path, min_size)
    lines = wrap(draw, s, fnt, width)[:max_lines]
    if lines:
        last = lines[-1]
        while last and text_w(draw, last + "…", fnt) > width:
            last = last[:-1]
        lines[-1] = last + "…" if last else "…"
    return fnt, lines


def fit_single(draw, s, path, start_size, width, min_size=9):
    """Single line: shrink until it fits the width. Returns (font, text)."""
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        if text_w(draw, s, fnt) <= width:
            return fnt, s
        size -= 1
    fnt = font(path, min_size)
    out = s
    while out and text_w(draw, out + "…", fnt) > width:
        out = out[:-1]
    return fnt, out + "…" if out else "…"


def block(draw, x, y, lines, fnt, leading, fill):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def gradient(draw, x0, y0, x1, y1, top, bottom):
    """Vertical two-stop gradient, drawn line by line (deterministic)."""
    h = max(1, y1 - y0)
    for yy in range(y0, y1):
        t = (yy - y0) / h
        col = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(x0, yy), (x1, yy)], fill=col)


def lerp(top, bottom, t):
    return tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
