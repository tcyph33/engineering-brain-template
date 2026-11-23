"""Tests for finding `@path` imports in the always-loaded files that lead nowhere."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.missing_imports import find_missing_imports
from damage import Damage, Severity
from scratch_brain import ScratchBrain


class MissingImportsTest(unittest.TestCase):
    """Which imports are missing."""

    def test_import_of_a_missing_note_is_reported(self) -> None:
        """An import must name a note in the brain."""
        # Load a brain whose README imports a missing note
        brain: Brain = ScratchBrain.load(self, {"README.md": "@principles/README.md\n"})

        # Expect it reported at the importer
        self.assertEqual(find_missing_imports(brain), [Damage(
            Severity.ERROR,
            "README.md",
            "imports principles/README.md, which isn't a note in the brain",
        )])

    def test_missing_import_in_an_imported_note_is_reported(self) -> None:
        """Imports are followed through the notes the README imports."""
        # Load a brain whose imported note imports a missing one
        brain: Brain = ScratchBrain.load(self, {
            "README.md": "@principles/README.md\n",
            "principles/README.md": "@missing.md\n",
        })

        # Expect it reported at the imported note, resolved from its folder
        self.assertEqual(find_missing_imports(brain), [Damage(
            Severity.ERROR,
            "principles/README.md",
            "imports principles/missing.md, which isn't a note in the brain",
        )])

    def test_brain_without_a_root_readme_is_reported(self) -> None:
        """Everything always loaded starts from the root README."""
        # Load a brain with no root README
        brain: Brain = ScratchBrain.load(self, {"principles/README.md": "# Principles\n"})

        # Expect it reported
        self.assertEqual(find_missing_imports(brain), [Damage(
            Severity.ERROR,
            "README.md",
            "the brain has no root README, so nothing in it loads",
        )])

    def test_imports_inside_sentences_and_before_punctuation_are_followed(self) -> None:
        """An import may sit in a sentence and end before a full stop."""
        # Load a brain whose README imports in a sentence
        brain: Brain = ScratchBrain.load(self, {
            "README.md": "Load (@principles/README.md) and @lessons.md.\n",
            "principles/README.md": "# Principles\n",
            "lessons.md": "# Lessons\n",
        })

        # Expect nothing reported
        self.assertEqual(find_missing_imports(brain), [])

    def test_at_sign_inside_a_word_or_code_is_not_an_import(self) -> None:
        """Email addresses and code aren't imports."""
        # Load a brain whose README has an email address and an import in code
        brain: Brain = ScratchBrain.load(
            self, {"README.md": "Mail me@example.com.\n\n`@missing.md`\n"}
        )

        # Expect nothing reported
        self.assertEqual(find_missing_imports(brain), [])

    def test_notes_importing_each_other_are_followed_once(self) -> None:
        """An import cycle ends rather than looping."""
        # Load a brain whose notes import each other
        brain: Brain = ScratchBrain.load(self, {
            "README.md": "@principles/README.md\n",
            "principles/README.md": "@../README.md\n",
        })

        # Expect the check to finish with nothing reported
        self.assertEqual(find_missing_imports(brain), [])
