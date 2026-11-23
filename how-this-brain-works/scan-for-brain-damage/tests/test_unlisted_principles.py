"""Tests for finding principle files the principles README doesn't link to."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.unlisted_principles import find_unlisted_principles
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# A principle file's contents.
PRINCIPLE_FILE_TEXT: str = "---\nread-when: Always.\n---\n# How to apply it\n"


class UnlistedPrinciplesTest(unittest.TestCase):
    """Which principle files are unlisted."""

    def test_principle_file_the_readme_does_not_link_to_is_reported(self) -> None:
        """Every principle file is linked from the always-loaded README."""
        # Load a brain whose README lists one of two principle files
        brain: Brain = ScratchBrain.load(self, {
            "principles/README.md": "- **Listed.** [How to apply it](listed.md)\n",
            "principles/listed.md": PRINCIPLE_FILE_TEXT,
            "principles/unlisted.md": PRINCIPLE_FILE_TEXT,
        })

        # Expect only the unlisted one reported
        self.assertEqual(find_unlisted_principles(brain), [Damage(
            Severity.ERROR,
            "principles/unlisted.md",
            "no principle in principles/README.md links to this file",
        )])

    def test_missing_principles_readme_is_reported(self) -> None:
        """The README that lists the principles must exist."""
        # Load a brain with no principles README
        brain: Brain = ScratchBrain.load(self, {"principles/an-idea.md": PRINCIPLE_FILE_TEXT})

        # Expect it reported
        self.assertEqual(find_unlisted_principles(brain), [Damage(
            Severity.ERROR,
            "principles/README.md",
            "is missing; it lists every principle",
        )])
