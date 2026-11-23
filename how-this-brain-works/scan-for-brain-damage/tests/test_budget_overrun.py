"""Tests for keeping the always-loaded files within their line budget."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.budget_overrun import find_budget_overrun
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# How many lines the always-loaded files may total.
LINE_BUDGET: int = 150


def _text_of_lines(line_count: int) -> str:
    """Text of exactly the given number of lines.

    Args:
        line_count: How many lines.

    Returns:
        That many short lines.
    """
    # Repeat one line
    text: str = ("line\n" * line_count)
    return text


def _overrun_damage(line_count: int) -> list[Damage]:
    """The damage reported when the always-loaded files total too many lines.

    Args:
        line_count: Their total.

    Returns:
        The one error the check gives.
    """
    # Build the expected error at the root README
    damage: list[Damage] = [Damage(
        Severity.ERROR,
        "README.md",
        f"the always-loaded files total {line_count} lines, over the {LINE_BUDGET}-line "
        "budget; see 'How it's read' in the manual",
    )]
    return damage


class BudgetOverrunTest(unittest.TestCase):
    """When the always-loaded files run over budget."""

    def test_files_exactly_at_the_budget_are_fine(self) -> None:
        """The budget itself is allowed."""
        # Load a brain whose README is exactly at the budget
        brain: Brain = ScratchBrain.load(self, {"README.md": _text_of_lines(LINE_BUDGET)})

        # Expect nothing reported
        self.assertEqual(find_budget_overrun(brain), [])

    def test_one_line_over_the_budget_is_reported(self) -> None:
        """A line past the budget is an error at the root README."""
        # Load a brain whose README is one line over
        brain: Brain = ScratchBrain.load(self, {"README.md": _text_of_lines((LINE_BUDGET + 1))})

        # Expect it reported
        self.assertEqual(find_budget_overrun(brain), _overrun_damage((LINE_BUDGET + 1)))

    def test_imported_files_count_toward_the_budget(self) -> None:
        """Lines in imported notes add to the README's."""
        # Load a brain whose README and imported note together run one line over
        README_LINE_COUNT: int = 100
        readme_text: str = "@principles/README.md\n" + _text_of_lines((README_LINE_COUNT - 1))
        imported_text: str = _text_of_lines(((LINE_BUDGET + 1) - README_LINE_COUNT))
        brain: Brain = ScratchBrain.load(
            self, {"README.md": readme_text, "principles/README.md": imported_text}
        )

        # Expect the total reported
        self.assertEqual(find_budget_overrun(brain), _overrun_damage((LINE_BUDGET + 1)))

    def test_notes_that_are_not_imported_do_not_count(self) -> None:
        """Only always-loaded files count toward the budget."""
        # Load a brain with a long note nothing imports
        brain: Brain = ScratchBrain.load(self, {
            "README.md": "# Brain\n",
            "lessons-learned/README.md": _text_of_lines(LINE_BUDGET),
        })

        # Expect nothing reported
        self.assertEqual(find_budget_overrun(brain), [])
