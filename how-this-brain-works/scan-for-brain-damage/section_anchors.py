"""Section anchors: the anchors GitHub gives a note's headings, which links can point at."""

from __future__ import annotations

import re
from typing import Optional, cast


def section_anchors(text_without_code_blocks: str) -> frozenset[str]:
    """Works out the section anchors GitHub generates for a note's headings.

    Repeated headings get GitHub's suffixes: the second "Why" is "why-1", the third "why-2".

    Args:
        text_without_code_blocks: The note's text with fenced code removed, inline code kept.

    Returns:
        Every anchor a link into the note can use.
    """
    # Slug each heading, in document order, numbering repeats the way GitHub does
    anchors: set[str] = set()
    times_seen: dict[str, int] = {}
    heading: str
    for heading in _headings_in(text_without_code_blocks):
        base_anchor: str = _heading_to_anchor(heading)
        repeat_count: int = times_seen.get(base_anchor, 0)
        is_first_occurrence: bool = (repeat_count == 0)
        anchor: str = base_anchor if is_first_occurrence else f"{base_anchor}-{repeat_count}"
        anchors.add(anchor)
        times_seen[base_anchor] = (repeat_count + 1)
    heading_anchors: frozenset[str] = frozenset(anchors)
    return heading_anchors


def _headings_in(text: str) -> list[str]:
    """Finds a note's headings, in document order.

    Two forms count: ATX headings (up to 3 spaces, 1-6 '#', the text, optional closing
    '#'s) and setext headings (a line of text underlined with '=' or '-').

    Args:
        text: The note's text with fenced code removed.

    Returns:
        Each heading's text, without its markers.
    """
    # Walk the lines, checking each for an ATX heading or a setext underline below it
    ATX_HEADING_PATTERN: re.Pattern[str] = re.compile(
        r"""
        [ ]{0,3}\#{1,6}[ \t]+    # indentation and opening hashes
        (?P<text>.+?)            # the heading's text
        (?:[ \t]+\#+)?[ \t]*     # optional closing hashes
        """,
        flags=re.VERBOSE,
    )
    SETEXT_UNDERLINE_PATTERN: re.Pattern[str] = re.compile(r"[ ]{0,3}(?:=+|-+)[ \t]*")
    NOT_SETEXT_TEXT_PATTERN: re.Pattern[str] = re.compile(r"\s*(?:$|[-*+>#|]|\d+[.)]\s)")
    lines: list[str] = text.split("\n")
    headings: list[str] = []
    line_index: int
    for line_index in range(len(lines)):
        line: str = lines[line_index]

        # An ATX heading is its own line
        atx_match: Optional[re.Match[str]] = ATX_HEADING_PATTERN.fullmatch(line)
        is_atx_heading: bool = (atx_match is not None)
        if is_atx_heading:
            headings.append(cast(re.Match[str], atx_match).group("text"))
            continue

        # A setext heading is a line of paragraph text with an underline below it
        has_next_line: bool = ((line_index + 1) < len(lines))
        next_line: str = lines[line_index + 1] if has_next_line else ""
        is_next_line_underline: bool = (SETEXT_UNDERLINE_PATTERN.fullmatch(next_line) is not None)
        is_underlined: bool = (has_next_line and is_next_line_underline)
        is_paragraph_text: bool = (NOT_SETEXT_TEXT_PATTERN.match(line) is None)
        is_setext_heading: bool = (is_underlined and is_paragraph_text)
        if is_setext_heading:
            headings.append(line.strip())
    return headings


def _heading_to_anchor(heading: str) -> str:
    """Converts a heading to the anchor slug GitHub gives it.

    GitHub slugs the rendered text: links become their text and emphasis marks disappear,
    while underscores inside words (snake_case) stay. It then lowercases, drops punctuation
    (keeping letters in any language, digits, underscores, hyphens, and spaces), and turns
    spaces into hyphens.

    Args:
        heading: The heading text, without the '#' marks.

    Returns:
        The slug.
    """
    # Reduce the heading to the text GitHub renders
    LINK_PATTERN: re.Pattern[str] = re.compile(r"\[([^\]]*)\]\([^)]*\)")
    EMPHASIS_UNDERSCORE_PATTERN: re.Pattern[str] = re.compile(r"(?<!\w)_+|_+(?!\w)")
    MARKUP_PATTERN: re.Pattern[str] = re.compile(r"[*`~]")
    rendered_heading: str = LINK_PATTERN.sub(r"\1", heading.strip())
    rendered_heading = EMPHASIS_UNDERSCORE_PATTERN.sub("", rendered_heading)
    rendered_heading = MARKUP_PATTERN.sub("", rendered_heading)

    # Lowercase, drop punctuation, and hyphenate spaces
    PUNCTUATION_PATTERN: re.Pattern[str] = re.compile(r"[^\w\- ]")
    without_punctuation: str = PUNCTUATION_PATTERN.sub("", rendered_heading.lower())
    anchor: str = without_punctuation.replace(" ", "-")
    return anchor
