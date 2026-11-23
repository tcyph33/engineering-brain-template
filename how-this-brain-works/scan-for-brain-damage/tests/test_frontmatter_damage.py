"""Tests for finding frontmatter that's unreadable, missing, not allowed, or missing or
carrying the wrong fields for its kind of note."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.frontmatter_damage import find_frontmatter_damage
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# A decision record's path.
DECISION_PATH: str = "how-this-brain-works/decisions/0001-a-decision.md"


class FrontmatterPresenceDamageTest(unittest.TestCase):
    """Frontmatter present exactly where the note's kind needs it, and readable."""

    def test_decision_without_frontmatter_is_reported(self) -> None:
        """A decision record needs frontmatter."""
        # Load a brain with a bare decision record
        brain: Brain = ScratchBrain.load(self, {DECISION_PATH: "# A decision\n"})

        # Expect it reported
        self.assertEqual(
            find_frontmatter_damage(brain),
            [Damage(Severity.ERROR, DECISION_PATH, "a decision record needs frontmatter")],
        )

    def test_folder_readme_with_frontmatter_is_reported(self) -> None:
        """A folder README has no frontmatter."""
        # Load a brain whose principles README has frontmatter
        brain: Brain = ScratchBrain.load(
            self, {"principles/README.md": "---\nsummary: One line.\n---\n# Principles\n"}
        )

        # Expect it reported
        self.assertEqual(
            find_frontmatter_damage(brain),
            [Damage(Severity.ERROR, "principles/README.md", "a folder README has no frontmatter")],
        )

    def test_unreadable_frontmatter_is_reported_with_its_problem(self) -> None:
        """Frontmatter that can't be read is an error saying why."""
        # Load a brain with a quoted value
        brain: Brain = ScratchBrain.load(
            self, {DECISION_PATH: '---\nsummary: "One line."\nread-when: Always.\n---\n'}
        )

        # Expect the reading problem as the description
        self.assertEqual(
            find_frontmatter_damage(brain),
            [Damage(
                Severity.ERROR,
                DECISION_PATH,
                "'\"One line.\"' starts with '\"', which YAML reads as syntax rather than text; "
                "write the value plainly, without quotes, brackets, blocks, or markup at its "
                "start; see 'Note format' in how-this-brain-works/README.md",
            )],
        )

    def test_note_in_a_place_the_manual_does_not_define_is_left_alone(self) -> None:
        """Misplaced notes are the misplaced-files check's to report."""
        # Load a brain with a bare note in an unknown place
        brain: Brain = ScratchBrain.load(self, {"notes/idea.md": "# Idea\n"})

        # Expect nothing reported here
        self.assertEqual(find_frontmatter_damage(brain), [])


class FrontmatterFieldDamageTest(unittest.TestCase):
    """The fields a kind of note requires and allows."""

    def test_missing_required_field_is_reported(self) -> None:
        """A decision record without read-when names the missing field."""
        # Load a brain whose decision has only a summary
        brain: Brain = ScratchBrain.load(self, {DECISION_PATH: "---\nsummary: One line.\n---\n"})

        # Expect the field named
        self.assertEqual(
            find_frontmatter_damage(brain),
            [Damage(Severity.ERROR, DECISION_PATH, "a decision record needs read-when")],
        )

    def test_empty_required_field_is_reported(self) -> None:
        """A required field written with no value counts as missing."""
        # Load a brain whose decision leaves read-when empty
        brain: Brain = ScratchBrain.load(
            self, {DECISION_PATH: "---\nsummary: One line.\nread-when:\n---\n"}
        )

        # Expect the field named
        self.assertEqual(
            find_frontmatter_damage(brain),
            [Damage(Severity.ERROR, DECISION_PATH, "a decision record needs read-when")],
        )

    def test_extra_field_on_a_principle_file_is_reported(self) -> None:
        """A principle file has only read-when."""
        # Load a brain whose principle file also has a summary
        brain: Brain = ScratchBrain.load(self, {
            "principles/an-idea.md": "---\nsummary: One line.\nread-when: Always.\n---\n"
        })

        # Expect the extra field named
        self.assertEqual(
            find_frontmatter_damage(brain),
            [Damage(
                Severity.ERROR,
                "principles/an-idea.md",
                "a principle file has only read-when; remove summary",
            )],
        )

    def test_optional_field_on_a_lesson_is_allowed(self) -> None:
        """Kinds with optional fields accept more than their required ones."""
        # Load a brain whose lesson also has a status
        brain: Brain = ScratchBrain.load(self, {
            "lessons-learned/a-lesson.md": (
                "---\nsummary: One line.\nread-when: Always.\noccurrences:\n"
                "  - 2026-11-22 in owner/name\nstatus: active\n---\n"
            ),
        })

        # Expect nothing reported
        self.assertEqual(find_frontmatter_damage(brain), [])
