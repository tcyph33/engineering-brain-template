"""Link: a relative link from one note to a file or section in the brain."""

from __future__ import annotations

import posixpath
import re
import urllib.parse
from dataclasses import dataclass


@dataclass(frozen=True)
class Link:
    """A relative link from one note to a file or section in the brain.

    Attributes:
        target: The linked path, URL-decoded: relative to the note, or to the brain's root
            when it starts with '/'; empty for a section of the same note.
        anchor: The linked section's anchor, without '#'; empty for the whole file.
    """

    target: str
    anchor: str

    @classmethod
    def all_in(cls, readable_text: str) -> tuple[Link, ...]:
        """Finds a note's links into the brain, inline (`[text](path)`) and by reference
        (`[label]: path`), leaving out links with a scheme (https:, mailto:, tel:, and so
        on) and the manual's "..." placeholders.

        Args:
            readable_text: The note's text with code removed.

        Returns:
            Each link into the brain, inline links first, with its target and anchor
            URL-decoded.
        """
        # Find every inline link, with or without a "title", and every reference definition
        MARKDOWN_LINK_PATTERN: re.Pattern[str] = re.compile(
            r"""
            \[(?:[^\[\]]|\[[^\]]*\])*\]    # [link text], which may hold [brackets]
            \(                             # (
            (?:<(?P<bracketed>[^>]*)>       #   <destination>, which may hold spaces
            |(?P<destination>[^)\s]+))     #   or destination
            (?:\s+"[^"]*")?                #   optional "title"
            \)                             # )
            """,
            flags=re.VERBOSE,
        )
        REFERENCE_DEFINITION_PATTERN: re.Pattern[str] = re.compile(
            r"""
            ^[ ]{0,3}\[[^\]]+\]:[ \t]*       # [label]:
            (?:<(?P<bracketed>[^>]*)>       # <destination>
            |(?P<destination>\S+))          # or destination
            """,
            flags=(re.MULTILINE | re.VERBOSE),
        )
        link_matches: list[re.Match[str]] = (
            list(MARKDOWN_LINK_PATTERN.finditer(readable_text))
            + list(REFERENCE_DEFINITION_PATTERN.finditer(readable_text))
        )
        links: list[Link] = []
        link_match: re.Match[str]
        for link_match in link_matches:
            # Skip links that go outside the brain by scheme, and the manual's placeholders
            SCHEME_PATTERN: re.Pattern[str] = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
            PLACEHOLDER_DESTINATION: str = "..."
            is_bracketed: bool = (link_match.group("bracketed") is not None)
            destination: str = (
                link_match.group("bracketed") if is_bracketed else link_match.group("destination")
            )
            has_scheme: bool = (SCHEME_PATTERN.match(destination) is not None)
            is_placeholder: bool = (destination == PLACEHOLDER_DESTINATION)
            is_skipped: bool = (has_scheme or is_placeholder)
            if is_skipped:
                continue

            # Split the destination into its file and section
            ANCHOR_SEPARATOR: str = "#"
            target: str
            anchor: str
            target, _, anchor = destination.partition(ANCHOR_SEPARATOR)
            links.append(cls(
                target=urllib.parse.unquote(target), anchor=urllib.parse.unquote(anchor)
            ))

        # Freeze the list
        relative_links: tuple[Link, ...] = tuple(links)
        return relative_links

    def path_from(self, note_path: str) -> str:
        """The brain-relative path this link leads to, from the note it's in.

        Args:
            note_path: The brain-relative path of the note the link is in.

        Returns:
            The normalized path; it starts with "../" when the link leaves the brain.
        """
        # A '/' target starts at the brain's root, another starts at the note's folder, and
        # an empty one is the note itself
        ROOT_PREFIX: str = "/"
        is_root_relative: bool = (self.target.startswith(ROOT_PREFIX))
        is_same_note: bool = (self.target == "")
        linked_path: str
        if is_root_relative:
            linked_path = posixpath.normpath(self.target.lstrip(ROOT_PREFIX))
        elif is_same_note:
            linked_path = note_path
        else:
            joined_path: str = posixpath.join(posixpath.dirname(note_path), self.target)
            linked_path = posixpath.normpath(joined_path)
        return linked_path
