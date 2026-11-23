"""Tests for warning about notes quarantined by their status."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.quarantined_notes import find_quarantined_notes
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# Where each test's note lives.
NOTE_PATH: str = "projects/a/dependencies/a-thing.md"


def _note_with_status(status: str) -> str:
    """A note whose only field is the given status.

    Args:
        status: The status value.

    Returns:
        The note's full contents.
    """
    # Write the status into frontmatter
    note_text: str = f"---\nstatus: {status}\n---\n"
    return note_text


class QuarantinedNotesTest(unittest.TestCase):
    """Which statuses quarantine a note."""

    def test_stale_note_is_warned_about(self) -> None:
        """A stale note needs verifying or fixing."""
        # Load a brain with a stale note
        brain: Brain = ScratchBrain.load(self, {NOTE_PATH: _note_with_status("stale")})

        # Expect a warning
        self.assertEqual(find_quarantined_notes(brain), [Damage(
            Severity.WARNING, NOTE_PATH, "is quarantined (status: stale); verify it or fix it"
        )])

    def test_unverified_note_is_warned_about(self) -> None:
        """An unverified note needs verifying."""
        # Load a brain with an unverified note
        brain: Brain = ScratchBrain.load(self, {NOTE_PATH: _note_with_status("unverified")})

        # Expect a warning
        self.assertEqual(find_quarantined_notes(brain), [Damage(
            Severity.WARNING,
            NOTE_PATH,
            "is quarantined (status: unverified); verify it or fix it",
        )])

    def test_active_note_is_not_warned_about(self) -> None:
        """An active note is trusted."""
        # Load a brain with an active note
        brain: Brain = ScratchBrain.load(self, {NOTE_PATH: _note_with_status("active")})

        # Expect nothing reported
        self.assertEqual(find_quarantined_notes(brain), [])
