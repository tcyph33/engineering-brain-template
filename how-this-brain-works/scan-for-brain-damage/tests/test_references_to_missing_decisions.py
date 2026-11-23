"""Tests for finding references to decision numbers no decision record has."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.references_to_missing_decisions import find_references_to_missing_decisions
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# The note each test's references are in.
REFERRING_NOTE_PATH: str = "lessons-learned/README.md"


def _references_in(test_case: unittest.TestCase, referring_text: str) -> list[Damage]:
    """Finds references to missing decisions in a brain whose only decision is 0001.

    Args:
        test_case: The test the brain is for.
        referring_text: The referring note's full contents.

    Returns:
        What the check reports.
    """
    # Load a brain with decision 0001 and the referring note, and check it
    brain: Brain = ScratchBrain.load(test_case, {
        "how-this-brain-works/decisions/0001-first.md": "# First\n",
        REFERRING_NOTE_PATH: referring_text,
    })
    damage: list[Damage] = find_references_to_missing_decisions(brain)
    return damage


class ReferencesToMissingDecisionsTest(unittest.TestCase):
    """Which numbers count as references, and which are missing."""

    def test_reference_to_a_missing_decision_is_reported(self) -> None:
        """A number no decision record has is an error."""
        # Check a note that refers to 0099
        damage: list[Damage] = _references_in(self, "See 0099.\n")

        # Expect it reported
        self.assertEqual(damage, [Damage(
            Severity.ERROR, REFERRING_NOTE_PATH, "refers to decision 0099, which doesn't exist"
        )])

    def test_reference_to_an_existing_decision_is_fine(self) -> None:
        """A number a decision record has is fine."""
        # Check a note that refers to 0001
        damage: list[Damage] = _references_in(self, "See 0001.\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_number_in_version_is_not_a_reference(self) -> None:
        """A number in a version number isn't a decision reference."""
        # Check a note with 0099 in a version number
        damage: list[Damage] = _references_in(self, "Version 1.0099 is out.\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_number_in_file_name_is_not_a_reference(self) -> None:
        """A number in a file name isn't a decision reference."""
        # Check a note with 0099 in a file name
        damage: list[Damage] = _references_in(self, "See file 0099-a.md.\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_number_in_time_is_not_a_reference(self) -> None:
        """A number in a time isn't a decision reference."""
        # Check a note with 0099 in a time
        damage: list[Damage] = _references_in(self, "Meet at 12:0099.\n")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_number_in_code_is_not_a_reference(self) -> None:
        """A number in code isn't a decision reference."""
        # Check a note with 0099 in code
        damage: list[Damage] = _references_in(self, "Run `0099` first.\n")

        # Expect nothing reported
        self.assertEqual(damage, [])
