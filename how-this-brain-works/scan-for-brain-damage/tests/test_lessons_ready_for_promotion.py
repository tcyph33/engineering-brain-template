"""Tests for suggesting promotion of lessons that keep recurring."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.lessons_ready_for_promotion import find_lessons_ready_for_promotion
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# Where each test's lesson lives.
LESSON_PATH: str = "lessons-learned/a-lesson.md"


def _note_with_occurrences(occurrence_count: int) -> str:
    """A note listing the given number of occurrences.

    Args:
        occurrence_count: How many occurrences to list.

    Returns:
        The note's full contents.
    """
    # List one occurrence per line, each on its own day
    occurrence_lines: list[str] = []
    occurrence_day: int
    for occurrence_day in range(1, (occurrence_count + 1)):
        occurrence_lines.append(f"  - 2026-11-{occurrence_day:02d} in owner/name\n")
    note_text: str = "---\noccurrences:\n" + "".join(occurrence_lines) + "---\n"
    return note_text


class LessonsReadyForPromotionTest(unittest.TestCase):
    """When a lesson has recurred enough to promote."""

    def test_lesson_with_three_occurrences_is_suggested_for_promotion(self) -> None:
        """Three occurrences is the threshold."""
        # Load a brain with a lesson seen three times
        brain: Brain = ScratchBrain.load(self, {LESSON_PATH: _note_with_occurrences(3)})

        # Expect a warning
        self.assertEqual(find_lessons_ready_for_promotion(brain), [Damage(
            Severity.WARNING,
            LESSON_PATH,
            "has 3 occurrences; suggest promoting it (see 'Lessons')",
        )])

    def test_lesson_with_two_occurrences_is_not_suggested(self) -> None:
        """Below the threshold, the lesson stays."""
        # Load a brain with a lesson seen twice
        brain: Brain = ScratchBrain.load(self, {LESSON_PATH: _note_with_occurrences(2)})

        # Expect nothing reported
        self.assertEqual(find_lessons_ready_for_promotion(brain), [])

    def test_note_that_is_not_a_lesson_is_not_suggested(self) -> None:
        """Only lessons are promoted, whatever fields another note has."""
        # Load a brain with a dependency note listing three occurrences
        brain: Brain = ScratchBrain.load(
            self, {"projects/a/dependencies/a-thing.md": _note_with_occurrences(3)}
        )

        # Expect nothing reported
        self.assertEqual(find_lessons_ready_for_promotion(brain), [])
