"""Tests for finding pointers that don't fit the manual's pointer format."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.malformed_pointers import find_malformed_pointers
from damage import Damage, Severity
from note_with_frontmatter import note_with_frontmatter
from scratch_brain import ScratchBrain

# Where each test's note lives.
NOTE_PATH: str = "projects/a/dependencies/a-thing.md"


def _damage_for_pointer(test_case: unittest.TestCase, *pointer_lines: str) -> list[Damage]:
    """Finds the malformed-pointer damage in a note with the given pointers.

    Args:
        test_case: The test the brain is for.
        pointer_lines: The lines under the note's pointers field.

    Returns:
        What the check reports.
    """
    # Load a brain whose one note has these pointers, and check it
    brain: Brain = ScratchBrain.load(
        test_case, {NOTE_PATH: note_with_frontmatter("pointers:", *pointer_lines)}
    )
    damage: list[Damage] = find_malformed_pointers(brain)
    return damage


def _malformed_pointer_damage(reason: str) -> list[Damage]:
    """The damage reported for one malformed pointer in the test's note.

    Args:
        reason: Why the pointer is malformed.

    Returns:
        The one error the check gives it.
    """
    # Build the expected error
    damage: list[Damage] = [Damage(Severity.ERROR, NOTE_PATH, f"{reason}; see 'Note format'")]
    return damage


class MalformedPointersTest(unittest.TestCase):
    """Which pointers are malformed, and why."""

    def test_pointer_written_as_a_plain_value_is_malformed(self) -> None:
        """Each pointer is a map of fields."""
        # Check a plain-value pointer
        damage: list[Damage] = _damage_for_pointer(self, "  - owner/name/path")

        # Expect it reported
        self.assertEqual(
            damage,
            _malformed_pointer_damage("a pointer must be a map of fields, not 'owner/name/path'"),
        )

    def test_pointer_with_neither_repo_nor_url_is_malformed(self) -> None:
        """A pointer needs a repository or a URL to point at."""
        # Check a pointer with only a description
        damage: list[Damage] = _damage_for_pointer(self, "  - what: The thing")

        # Expect it reported
        self.assertEqual(
            damage,
            _malformed_pointer_damage(
                "each pointer needs repo and path, or url"
            ),
        )

    def test_repo_that_is_not_owner_and_name_is_malformed(self) -> None:
        """A repo is written owner/name."""
        # Check a pointer with a bare repo name
        damage: list[Damage] = _damage_for_pointer(self, "  - repo: only-name", "    path: a.py")

        # Expect it reported
        self.assertEqual(
            damage,
            _malformed_pointer_damage(
                "pointer repo must be owner/name, not 'only-name'"
            ),
        )

    def test_repo_pointer_without_a_path_is_malformed(self) -> None:
        """A repository pointer names a file in it."""
        # Check a pointer with no path
        damage: list[Damage] = _damage_for_pointer(self, "  - repo: owner/name")

        # Expect it reported
        self.assertEqual(damage, _malformed_pointer_damage("pointer to owner/name needs a path"))

    def test_verified_stamp_without_a_date_is_malformed(self) -> None:
        """A verified stamp starts with a YYYY-MM-DD date."""
        # Check a pointer verified "yesterday"
        damage: list[Damage] = _damage_for_pointer(
            self, "  - repo: owner/name", "    path: a.py", "    verified: yesterday"
        )

        # Expect it reported
        self.assertEqual(
            damage,
            _malformed_pointer_damage(
                "verified must start with a YYYY-MM-DD date, not 'yesterday'"
            ),
        )

    def test_verified_commit_that_is_not_hex_is_malformed(self) -> None:
        """The commit after '@' is a hex hash."""
        # Check a pointer verified at a made-up commit
        damage: list[Damage] = _damage_for_pointer(
            self, "  - repo: owner/name", "    path: a.py", "    verified: 2026-11-22 @ main"
        )

        # Expect it reported
        self.assertEqual(
            damage,
            _malformed_pointer_damage(
                "verified commit must be a hex hash, not 'main'"
            ),
        )

    def test_well_formed_repository_pointer_is_not_reported(self) -> None:
        """A repository pointer in the template's shape is fine."""
        # Check a full repository pointer
        damage: list[Damage] = _damage_for_pointer(
            self,
            "  - what: The thing",
            "    repo: owner/name",
            "    path: a.py",
            "    verified: 2026-11-22 @ a1b2c3d",
        )

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_well_formed_web_pointer_is_not_reported(self) -> None:
        """A web pointer in the template's shape is fine."""
        # Check a web pointer
        damage: list[Damage] = _damage_for_pointer(
            self, "  - what: A doc", "    url: https://example.com/doc"
        )

        # Expect nothing reported
        self.assertEqual(damage, [])
