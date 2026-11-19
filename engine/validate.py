"""Content accounting for the news-image engine.

The 2026-11-17 page lost points for counts that contradicted each
other and figures that repeated. Here those are build failures, not
intentions. validate(content) raises ValueError on any of:

  * fewer than MIN_STORIES distinct stories, or duplicate ids;
  * a story with no region, headline or dek;
  * illustrated stories (tier hero/card, i.e. carrying a scene)
    outside the 12–13 band;
  * a scene name with no registered painter;
  * a numbers-strip figure that appears anywhere else in the page's
    text (headlines, deks, scene captions, in-scene labels) — the
    strip must be purely additive;
  * a strip figure whose story carries no strip_caption;
  * more than MAX_STRIP strip figures.
"""

MIN_STORIES = 43
MIN_SCENES = 12
MAX_SCENES = 13
MAX_STRIP = 6

# Editorial regions are finer than continents (the Middle East is a
# news region, not a continent). The scope line counts continents, so
# it goes through this mapping — printing "7 continents" for seven
# regions would be exactly the kind of false count NI17 was punished
# for.
CONTINENT_OF = {
    "Middle East": "Asia",
    "Asia": "Asia",
    "Europe": "Europe",
    "Africa": "Africa",
    "North America": "North America",
    "South America": "South America",
    "Oceania": "Oceania",
}


def _tokens(text):
    import re
    return {t for t in re.split(r"[^A-Za-z0-9]+", text.upper())
            if len(t) >= 4 and any(c.isalpha() for c in t)}


def _all_text(story):
    parts = [story.get("headline", ""), story.get("dek", ""),
             story.get("scene_caption", ""), story.get("place", "")]
    spec = story.get("scene_spec", {})
    parts.append(spec.get("label", ""))
    for flag in spec.get("flags", []):
        parts.append(flag[0])
    return " ".join(parts)


def illustrated(content):
    return [s for s in content["stories"] if s.get("scene")]


def validate(content):
    stories = content["stories"]
    ids = [s["id"] for s in stories]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate story ids")
    if len(stories) < MIN_STORIES:
        raise ValueError(f"only {len(stories)} distinct stories "
                         f"(< {MIN_STORIES})")
    for s in stories:
        for field in ("region", "headline", "dek", "place"):
            if not s.get(field):
                raise ValueError(f"story {s['id']} missing {field}")
        if s.get("tier") not in ("hero", "card"):
            # index stories print their brief, not their headline:
            # the brief is written to fit one line at full size, so
            # nothing on the page is silently truncated
            brief = s.get("brief", "")
            if not brief:
                raise ValueError(f"index story {s['id']} missing brief")
            if len(brief) > 50:
                raise ValueError(f"index story {s['id']} brief is "
                                 f"{len(brief)} chars (> 50)")
    scenes = illustrated(content)
    if not (MIN_SCENES <= len(scenes) <= MAX_SCENES):
        raise ValueError(f"{len(scenes)} illustrated stories "
                         f"(outside {MIN_SCENES}–{MAX_SCENES})")
    from .scenes import PAINTERS
    for s in scenes:
        if s["scene"] not in PAINTERS:
            raise ValueError(f"story {s['id']}: unknown painter "
                             f"{s['scene']!r}")
    heroes = [s for s in stories if s.get("tier") == "hero"]
    if len(heroes) != 1:
        raise ValueError(f"{len(heroes)} hero stories (need exactly 1)")
    strip = [s for s in stories if s.get("strip_figure")]
    if len(strip) > MAX_STRIP:
        raise ValueError(f"{len(strip)} strip figures (> {MAX_STRIP})")
    for s in strip:
        if not s.get("strip_caption"):
            raise ValueError(f"story {s['id']}: strip figure without "
                             "a strip_caption to anchor it")
        fig = s["strip_figure"]
        for other in stories:
            if fig in _all_text(other):
                raise ValueError(
                    f"strip figure {fig!r} (story {s['id']}) also "
                    f"appears in story {other['id']}'s text — the "
                    "strip would not be purely additive")
        # frame-level anchoring: the caption must share a content
        # word with the text the reader actually sees for that story
        # (headline for hero/cards, brief for the index) — a figure
        # whose fact lives only in an unprinted dek is an orphan
        printed = s["headline"] if s.get("tier") in ("hero", "card") \
            else s.get("brief", "")
        shared = _tokens(s["strip_caption"]) & _tokens(printed)
        if not shared:
            raise ValueError(
                f"strip caption for story {s['id']} shares no content "
                f"word with its printed line — the figure would be "
                f"an orphan on the page")
    regions = {s["region"] for s in stories}
    continents = {CONTINENT_OF.get(r, r) for r in regions}
    return {
        "stories": len(stories),
        "illustrated": len(scenes),
        "regions": len(regions),
        "continents": len(continents),
        "strip": len(strip),
    }


def scope_line(stats):
    """The quantified scope, computed from the content — never typed."""
    return (f"{stats['stories']} STORIES · {stats['continents']} CONTINENTS · "
            f"{stats['illustrated']} ILLUSTRATED")
