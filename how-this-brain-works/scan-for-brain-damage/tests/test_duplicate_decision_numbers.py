"""Tests for finding decision numbers used by more than one decision record."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.duplicate_decision_numbers import find_duplicate_decision_numbers
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# Where decision records live.
DECISIONS_FOLDER: str = "how-this-brain-works/decisions"


class DuplicateDecisionNumbersTest(unittest.TestCase):
    """Which decision numbers are duplicated."""

    def test_second_record_with_a_number_is_reported(self) -> None:
        """The later record, in path order, reuses the number."""
        # Load a brain with two records numbered 0001
        brain: Brain = ScratchBrain.load(self, {
            f"{DECISIONS_FOLDER}/0001-first.md": "# First\n",
            f"{DECISIONS_FOLDER}/0001-second.md": "# Second\n",
        })

        # Expect the second reported
        self.assertEqual(find_duplicate_decision_numbers(brain), [Damage(
            Severity.ERROR,
            f"{DECISIONS_FOLDER}/0001-second.md",
            "decision number 0001 is used twice",
        )])

    def test_records_with_different_numbers_are_not_reported(self) -> None:
        """Each number used once is fine, gaps included."""
        # Load a brain with records 0001 and 0003
        brain: Brain = ScratchBrain.load(self, {
            f"{DECISIONS_FOLDER}/0001-first.md": "# First\n",
            f"{DECISIONS_FOLDER}/0003-third.md": "# Third\n",
            f"{DECISIONS_FOLDER}/README.md": "# Decisions\n",
        })

        # Expect nothing reported
        self.assertEqual(find_duplicate_decision_numbers(brain), [])
