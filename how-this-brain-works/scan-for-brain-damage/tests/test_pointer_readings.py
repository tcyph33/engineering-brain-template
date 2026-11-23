"""Tests for reading a note's well-formed pointers into ones that can be checked."""

from __future__ import annotations

import unittest

from frontmatter import Frontmatter
from note_with_frontmatter import note_with_frontmatter
from pointer import Pointer
from pointer_readings import PointerReadings


def _read_pointers(*pointer_lines: str) -> PointerReadings:
    """Reads the pointers of frontmatter with the given pointer lines.

    Args:
        pointer_lines: The lines under the pointers field.

    Returns:
        The pointers, sorted by what can be done with them.
    """
    # Read the frontmatter, then its pointers
    note_text: str = note_with_frontmatter("pointers:", *pointer_lines)
    readings: PointerReadings = PointerReadings.read(Frontmatter.read(note_text))
    return readings


class PointerReadingsTest(unittest.TestCase):
    """What a well-formed pointer reads as."""

    def test_repository_pointer_is_read_with_every_field(self) -> None:
        """A full repository pointer keeps its description, target, symbol, and stamp."""
        # Read a full pointer
        readings: PointerReadings = _read_pointers(
            "  - what: The thing",
            "    repo: owner/name",
            "    path: src/thing.py",
            "    symbol: Thing",
            "    verified: 2026-11-22 @ a1b2c3d",
        )

        # Expect every field, with the stamp split into date and commit
        expected_pointer: Pointer = Pointer(
            description="The thing",
            repository="owner/name",
            path="src/thing.py",
            symbol="Thing",
            verified_stamp="2026-11-22 @ a1b2c3d",
            verified_date="2026-11-22",
            verified_commit="a1b2c3d",
        )
        self.assertEqual(readings.repository_pointers, (expected_pointer,))

    def test_stamp_with_only_a_date_has_no_commit(self) -> None:
        """A date-only stamp leaves the commit empty."""
        # Read a pointer verified on a date only
        readings: PointerReadings = _read_pointers(
            "  - repo: owner/name", "    path: a.py", "    verified: 2026-11-22"
        )

        # Expect no commit
        self.assertEqual(readings.repository_pointers[0].verified_commit, "")

    def test_web_pointer_is_neither_checked_nor_malformed(self) -> None:
        """A url-only pointer is well-formed but has nothing GitHub can check."""
        # Read a web pointer
        readings: PointerReadings = _read_pointers(
            "  - what: A doc", "    url: https://example.com/doc"
        )

        # Expect it in neither list
        self.assertEqual(readings, PointerReadings(repository_pointers=(), malformed_reasons=()))
