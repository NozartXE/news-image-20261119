"""The accounting gate for the front page.

validate(content) raises ValueError on the first broken rule it finds
and otherwise returns the stats dict the layout prints from. The rules
encode the fixed standard: one true story count, 12-13 illustrated
stories, exactly one hero, and a numbers strip that is purely additive
yet anchored to a printed line on the page.
"""

import re

REGION_TO_CONTINENT = {
    "Middle East": "Asia",
    "Asia": "Asia",
    "Europe": "Europe",
    "Africa": "Africa",
    "North America": "North America",
    "South America": "South America",
    "Oceania": "Oceania",
}

MIN_STORIES = 43
MIN_ILLUSTRATED = 12
MAX_ILLUSTRATED = 13
MAX_STRIP = 6
BRIEF_MIN = 1
BRIEF_MAX = 50

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokens(text):
    """Content tokens: alphanumeric runs of at least 4 characters."""
    return {t for t in _TOKEN.findall((text or "").lower()) if len(t) >= 4}


def _printed_texts(story):
    """Every string of this story that ends up printed on the page."""
    texts = [story.get("headline", ""), story.get("dek", ""),
             story.get("scene_caption", ""), story.get("place", "")]
    spec = story.get("scene_spec") or {}
    if spec.get("label"):
        texts.append(spec["label"])
    for flag in spec.get("flags") or []:
        texts.append(flag[0])
    return texts


def _printed_line(story):
    """The one line a reader sees for this story: headline for the
    illustrated tiers, the short brief for index stories."""
    if story.get("tier") in ("hero", "card"):
        return story.get("headline", "")
    return story.get("brief", "")


def validate(content):
    stories = content.get("stories")
    if not isinstance(stories, list):
        raise ValueError("content has no stories list")

    ids = [s.get("id") for s in stories]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate story ids")
    if len(set(ids)) < MIN_STORIES:
        raise ValueError("fewer than %d distinct stories" % MIN_STORIES)

    for story in stories:
        for field in ("region", "headline", "dek", "place"):
            if not (story.get(field) or "").strip():
                raise ValueError("story %s: empty %s" % (story.get("id"), field))
        if story.get("region") not in REGION_TO_CONTINENT:
            raise ValueError("story %s: unknown region %r"
                             % (story.get("id"), story.get("region")))
        if story.get("tier") not in ("hero", "card"):
            brief = story.get("brief") or ""
            if not (BRIEF_MIN <= len(brief) <= BRIEF_MAX):
                raise ValueError("story %s: index brief must be %d-%d chars"
                                 % (story.get("id"), BRIEF_MIN, BRIEF_MAX))

    heroes = [s for s in stories if s.get("tier") == "hero"]
    if len(heroes) != 1:
        raise ValueError("expected exactly 1 hero, found %d" % len(heroes))

    illustrated = [s for s in stories if s.get("scene")]
    if not (MIN_ILLUSTRATED <= len(illustrated) <= MAX_ILLUSTRATED):
        raise ValueError("illustrated count %d outside %d-%d"
                         % (len(illustrated), MIN_ILLUSTRATED, MAX_ILLUSTRATED))

    # Imported lazily so this module stays importable on its own.
    from .scenes import PAINTERS
    for story in illustrated:
        if story["scene"] not in PAINTERS:
            raise ValueError("story %s: unknown painter %r"
                             % (story.get("id"), story["scene"]))

    strip = [s for s in stories if s.get("strip_figure")]
    if len(strip) > MAX_STRIP:
        raise ValueError("too many strip figures: %d" % len(strip))

    all_printed = []
    for story in stories:
        all_printed.extend(_printed_texts(story))

    for story in strip:
        figure = story["strip_figure"]
        if not (story.get("strip_caption") or "").strip():
            raise ValueError("story %s: strip figure without caption"
                             % story.get("id"))
        for text in all_printed:
            if figure in text:
                raise ValueError(
                    "strip figure %r of story %s also appears in printed "
                    "text %r - the strip must be purely additive"
                    % (figure, story.get("id"), text))
        shared = _tokens(story["strip_caption"]) & _tokens(_printed_line(story))
        if not shared:
            raise ValueError(
                "story %s: strip caption shares no content token with its "
                "printed line - orphan figure" % story.get("id"))

    continents = {REGION_TO_CONTINENT[s["region"]] for s in stories}
    regions = {s["region"] for s in stories}
    return {
        "stories": len(stories),
        "illustrated": len(illustrated),
        "regions": len(regions),
        "continents": len(continents),
        "strip": len(strip),
    }


def scope_line(stats):
    """The masthead scope line, computed from the stats - never typed."""
    return "%d STORIES · %d CONTINENTS · %d ILLUSTRATED" % (
        stats["stories"], stats["continents"], stats["illustrated"])
