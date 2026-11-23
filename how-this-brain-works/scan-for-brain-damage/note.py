"""Note: one markdown file in the brain, read once and shaped for the checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, cast

from frontmatter import Frontmatter
from link import Link
from note_kind import DECISION_KIND, NoteKind
from pointer_readings import PointerReadings
from section_anchors import section_anchors


class NoteReadError(Exception):
    """Raised when a note's file can't be read as UTF-8 text."""


@dataclass(frozen=True)
class Note:
    """One markdown file in the brain, read and checked for shape once, when it's loaded.

    Attributes:
        path: The brain-relative path, with forward slashes.
        kind: The kind of note the manual says this path is; None when it defines no such
            place.
        frontmatter: The note's frontmatter, as read.
        readable_text: The text without code, where links and references are only examples.
        links: The note's links to other files and sections in the brain.
        anchors: The section anchors GitHub generates for the note's headings.
        line_count: How many lines the note has.
        pointers: The note's pointers, already checked for format.
    """

    path: str
    kind: Optional[NoteKind]
    frontmatter: Frontmatter
    readable_text: str
    links: tuple[Link, ...]
    anchors: frozenset[str]
    line_count: int
    pointers: PointerReadings

    @classmethod
    def read(cls, brain_root: Path, path: str) -> Note:
        """Reads a note from disk and works out everything the checks need from it.

        Args:
            brain_root: The brain's root folder.
            path: The note's brain-relative path.

        Returns:
            The note.

        Raises:
            NoteReadError: If the file can't be read as UTF-8 text.
        """
        # Read the note's text, dropping a byte-order mark; reading as text also turns
        # Windows line endings into Unix ones, since Windows editors often write both
        try:
            text: str = (brain_root / path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as error:
            raise NoteReadError(str(error)) from error

        # Work out everything the checks use
        frontmatter: Frontmatter = Frontmatter.read(text)
        text_without_code_blocks: str = _remove_code_blocks(text)
        readable_text: str = _remove_inline_code(text_without_code_blocks)
        note: Note = cls(
            path=path,
            kind=NoteKind.of(path),
            frontmatter=frontmatter,
            readable_text=readable_text,
            links=Link.all_in(readable_text),
            anchors=section_anchors(text_without_code_blocks),
            line_count=len(text.splitlines()),
            pointers=PointerReadings.read(frontmatter),
        )
        return note

    @property
    def status(self) -> str:
        """The note's status field.

        Returns:
            The status, or an empty string when the note has none.
        """
        # Read the status field
        STATUS_FIELD: str = "status"
        status: str = self.frontmatter.text(STATUS_FIELD)
        return status

    @property
    def occurrence_count(self) -> int:
        """How many occurrences a lesson lists.

        Returns:
            The number of occurrences, or 0 when the note lists none.
        """
        # Count the occurrences field's items
        OCCURRENCES_FIELD: str = "occurrences"
        count: int = len(self.frontmatter.items(OCCURRENCES_FIELD))
        return count

    @property
    def decision_number(self) -> Optional[str]:
        """The decision number in a decision record's file name.

        Returns:
            The four-digit number, or None when the note isn't a decision record.
        """
        # Ask the decision kind for the number in this path
        number: Optional[str] = DECISION_KIND.number_in(self.path)
        return number

    def missing_required_fields(self, kind: NoteKind) -> list[str]:
        """The fields a kind requires that this note leaves out or leaves empty.

        Args:
            kind: The kind of note this is.

        Returns:
            The missing field names, sorted.
        """
        # Collect required fields with no value
        missing_fields: list[str] = []
        required_field: str
        for required_field in sorted(kind.required_fields):
            is_filled: bool = (self.frontmatter.is_filled(required_field))
            if not is_filled:
                missing_fields.append(required_field)
        return missing_fields

    def fields_beyond(self, kind: NoteKind) -> list[str]:
        """The fields this note has that a kind doesn't require.

        Args:
            kind: The kind of note this is.

        Returns:
            The extra field names, sorted.
        """
        # Collect fields the kind doesn't require
        extra_fields: list[str] = []
        field_name: str
        for field_name in self.frontmatter.field_names():
            is_required: bool = (field_name in kind.required_fields)
            if not is_required:
                extra_fields.append(field_name)
        return extra_fields


def _remove_code_blocks(text: str) -> str:
    """Removes fenced code blocks, whose headings and links are only examples.

    A fence is three or more backticks or tildes; it closes at a line of the same character,
    at least as long, with nothing else on it. An unclosed fence runs to the end.

    Args:
        text: A note's full contents.

    Returns:
        The text without fenced code blocks.
    """
    # Keep lines outside fences, tracking the open fence
    FENCE_PATTERN: re.Pattern[str] = re.compile(r"^[ ]{0,3}(?P<fence>`{3,}|~{3,})")
    kept_lines: list[str] = []
    open_fence: str = ""
    line: str
    for line in text.split("\n"):
        fence_match: Optional[re.Match[str]] = FENCE_PATTERN.match(line)
        is_inside_fence: bool = (open_fence != "")
        is_fence_line: bool = (fence_match is not None)

        # Outside a fence, keep the line or open a fence
        if not is_inside_fence:
            if is_fence_line:
                open_fence = cast(re.Match[str], fence_match).group("fence")
            else:
                kept_lines.append(line)
            continue

        # Inside a fence, drop the line, closing the fence on a matching closer
        is_closing_fence: bool = (_is_closing_fence(line, open_fence))
        if is_closing_fence:
            open_fence = ""
    without_code_blocks: str = "\n".join(kept_lines)
    return without_code_blocks


def _is_closing_fence(line: str, open_fence: str) -> bool:
    """Whether a line closes an open fence.

    Args:
        line: A line inside a fenced block.
        open_fence: The fence that opened the block, such as "```" or "~~~~".

    Returns:
        True for a line of the same character, at least as long, and nothing else.
    """
    # Match the same character repeated at least as many times
    fence_character: str = re.escape(open_fence[0])
    closing_pattern: re.Pattern[str] = re.compile(
        rf"[ ]{{0,3}}{fence_character}{{{len(open_fence)},}}[ \t]*"
    )
    is_closing: bool = (closing_pattern.fullmatch(line) is not None)
    return is_closing


def _remove_inline_code(text: str) -> str:
    """Removes inline code, whose links and references are only examples.

    Args:
        text: A note's text, with code blocks already removed.

    Returns:
        The text without inline code.
    """
    # Drop everything between single backticks
    INLINE_CODE_PATTERN: re.Pattern[str] = re.compile(r"`[^`\n]*`")
    without_inline_code: str = INLINE_CODE_PATTERN.sub("", text)
    return without_inline_code
