"""Tests for reporting notes that can't be read as UTF-8 text."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.unreadable_notes import find_unreadable_notes
from damage import Damage, Severity
from scratch_brain import ScratchBrain


class UnreadableNotesTest(unittest.TestCase):
    """Which notes are reported as unreadable."""

    def test_note_that_is_not_utf8_is_reported(self) -> None:
        """A Latin-1 note is an error at its path, explaining it couldn't be checked."""
        # Load a brain with a Latin-1 note
        brain: Brain = ScratchBrain.load(self, {"lessons-learned/a-lesson.md": b"caf\xe9\n"})

        # Expect one error for it: the scan's own words, then Python's reason
        UNREADABLE_PREFIX: str = "isn't readable UTF-8 text, so it couldn't be checked: "
        damage: list[Damage] = find_unreadable_notes(brain)
        found_damage: Damage = damage[0]
        reason: str = found_damage.description[len(UNREADABLE_PREFIX):]
        self.assertEqual(
            (len(damage), found_damage.severity, found_damage.location),
            (1, Severity.ERROR, "lessons-learned/a-lesson.md"),
        )
        self.assertTrue(found_damage.description.startswith(UNREADABLE_PREFIX))
        self.assertNotEqual(reason.strip(), "")

    def test_utf8_note_is_not_reported(self) -> None:
        """A UTF-8 note, accents and all, is readable."""
        # Load a brain with an accented UTF-8 note
        brain: Brain = ScratchBrain.load(self, {"lessons-learned/a-lesson.md": "café\n"})

        # Expect nothing reported
        self.assertEqual(find_unreadable_notes(brain), [])
