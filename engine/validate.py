"""The accounting gate for the front page.

validate(content) raises ValueError on the first broken rule it finds
and otherwise returns the stats dict the layout prints from. The rules
encode the fixed standard: one true story count, 12-13 illustrated
stories, exactly one hero, a numbers strip whose every figure is
anchored verbatim in exactly one story's printed headline or dek,
continuous 1..N numbering, a region bar that sums to the story total,
complete-clause briefs, and no off-day figures anywhere on the page
(they belong only in the static DATE CHECK box, which is layout text,
never content).
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

REGION_ORDER = ["Asia", "Middle East", "Europe", "North America",
                "South America", "Africa", "Oceania"]

MIN_STORIES = 43
MIN_ILLUSTRATED = 12
MAX_ILLUSTRATED = 13
MAX_STRIP = 6
BRIEF_MIN = 1
BRIEF_MAX = 50

# Off-day material quarantined in the DATE CHECK box: it may never
# appear in any story's printed text.
BANNED_SUBSTRINGS = ("$115.8bn",)
BANNED_PATTERNS = (re.compile(r"\b561\b"), re.compile(r"jeffries", re.I))

# High-risk briefs (A11): each must carry at least two named sources.
MULTI_SOURCE_IDS = {24, 26, 27, 28}


def _printed_texts(story):
    """Every string of this story that ends up printed on the page."""
    texts = [story.get("headline", ""), story.get("dek", ""),
             story.get("scene_caption", ""), story.get("place", ""),
             story.get("brief", "")]
    spec = story.get("scene_spec") or {}
    if spec.get("label"):
        texts.append(spec["label"])
    for flag in spec.get("flags") or []:
        texts.append(flag[0])
    return texts


def story_order(stories):
    """Page order: the hero, then grid cards, then index briefs, each
    in content order. Numbering and the map follow this order."""
    hero = [s for s in stories if s.get("tier") == "hero"]
    cards = [s for s in stories if s.get("tier") == "card"]
    index = [s for s in stories if s.get("tier") not in ("hero", "card")]
    return hero + cards + index


def numbering(stories):
    """Story id -> printed number, continuous from 1 in page order."""
    return {s["id"]: n for n, s in enumerate(story_order(stories), start=1)}


def region_counts(stories):
    """Region -> story count, in the bar's fixed display order."""
    counts = {region: 0 for region in REGION_ORDER}
    for story in stories:
        counts[story["region"]] += 1
    return counts


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
            if brief[-1] not in ".!?":
                raise ValueError(
                    "story %s: brief %r does not end with terminal "
                    "punctuation - no brief may end mid-clause"
                    % (story.get("id"), brief))
        if story.get("id") in MULTI_SOURCE_IDS:
            if len(story.get("sources") or []) < 2:
                raise ValueError(
                    "story %s: high-risk brief needs at least 2 named "
                    "sources" % story.get("id"))

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

    # Numbering must be printed, continuous 1..N, no gaps or duplicates.
    expected = numbering(stories)
    printed = [s.get("num") for s in stories]
    if any(not isinstance(n, int) for n in printed):
        raise ValueError("every story must carry an integer num")
    if sorted(printed) != list(range(1, len(stories) + 1)):
        raise ValueError("numbering is not continuous 1-%d" % len(stories))
    for story in stories:
        if story["num"] != expected[story["id"]]:
            raise ValueError(
                "story %s: num %r does not match its page position %d"
                % (story.get("id"), story["num"], expected[story["id"]]))

    # The region bar must account for every story exactly once.
    counts = region_counts(stories)
    if sum(counts.values()) != len(stories):
        raise ValueError("region bar sums to %d, not the story total %d"
                         % (sum(counts.values()), len(stories)))

    # No off-day figure or name anywhere in a story's printed text.
    for story in stories:
        for text in _printed_texts(story):
            for banned in BANNED_SUBSTRINGS:
                if banned in text:
                    raise ValueError(
                        "story %s: off-day figure %r in printed text %r - "
                        "it belongs only in the DATE CHECK box"
                        % (story.get("id"), banned, text))
            for pattern in BANNED_PATTERNS:
                if pattern.search(text):
                    raise ValueError(
                        "story %s: off-day item %r in printed text %r - "
                        "it belongs only in the DATE CHECK box"
                        % (story.get("id"), pattern.pattern, text))

    # Every illustrated card's dek must carry a figure and a named source.
    for story in stories:
        if story.get("tier") == "card":
            dek = story.get("dek") or ""
            if "—" not in dek:
                raise ValueError(
                    "story %s: card dek carries no source attribution"
                    % story.get("id"))
            if not any(ch.isdigit() for ch in dek):
                raise ValueError(
                    "story %s: card dek carries no figure" % story.get("id"))

    strip = [s for s in stories if s.get("strip_figure")]
    if len(strip) > MAX_STRIP:
        raise ValueError("too many strip figures: %d" % len(strip))

    # Inverted strip rule: every strip figure must appear verbatim in
    # the headline or dek of exactly one story - its own anchor story.
    anchor_texts = {s["id"]: (s.get("headline", "") + "\n" + s.get("dek", ""))
                    for s in stories}
    for story in strip:
        figure = story["strip_figure"]
        if not (story.get("strip_caption") or "").strip():
            raise ValueError("story %s: strip figure without caption"
                             % story.get("id"))
        holders = [sid for sid, text in anchor_texts.items() if figure in text]
        if holders != [story["id"]]:
            raise ValueError(
                "strip figure %r of story %s must appear in exactly its "
                "own headline or dek; found in stories %r"
                % (figure, story.get("id"), holders))

    continents = {REGION_TO_CONTINENT[s["region"]] for s in stories}
    regions = {s["region"] for s in stories}
    return {
        "stories": len(stories),
        "illustrated": len(illustrated),
        "regions": len(regions),
        "continents": len(continents),
        "strip": len(strip),
        "region_counts": counts,
    }


def scope_line(stats):
    """The masthead scope line, computed from the stats - never typed."""
    return "%d STORIES · %d CONTINENTS · %d ILLUSTRATED" % (
        stats["stories"], stats["continents"], stats["illustrated"])
