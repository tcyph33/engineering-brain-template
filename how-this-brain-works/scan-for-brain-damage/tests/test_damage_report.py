"""Tests for printing what the scan found."""

from __future__ import annotations

import contextlib
import io
import unittest

from damage import Damage, Severity
from damage_report import print_damage_report


def _printed_report(damage: list[Damage]) -> str:
    """What the report prints for the given damage.

    Args:
        damage: Everything the scan found.

    Returns:
        The printed text.
    """
    # Capture the report's output
    output: io.StringIO = io.StringIO()
    with contextlib.redirect_stdout(output):
        print_damage_report(damage)
    printed_text: str = output.getvalue()
    return printed_text


class DamageReportTest(unittest.TestCase):
    """How the report reads."""

    def test_no_damage_says_so(self) -> None:
        """A clean brain gets one line."""
        # Print a report with nothing found
        report: str = _printed_report([])

        # Expect the all-clear
        self.assertEqual(report, "No brain damage found.\n")

    def test_errors_come_before_warnings_then_the_totals(self) -> None:
        """Errors are listed first, by path, then the counts and what to do."""
        # Print a report with a warning and two errors, out of order
        report: str = _printed_report([
            Damage(Severity.WARNING, "a.md", "needs a look"),
            Damage(Severity.ERROR, "c.md", "is broken"),
            Damage(Severity.ERROR, "b.md", "is broken"),
        ])

        # Expect errors by path, then the warning, then the totals
        self.assertEqual(report, (
            "error   b.md: is broken\n"
            "error   c.md: is broken\n"
            "warning a.md: needs a look\n"
            "\n"
            "2 errors, 1 warnings.\n"
            "Fix the errors before committing.\n"
        ))

    def test_warnings_alone_do_not_ask_for_fixes(self) -> None:
        """Warnings don't block a commit, so the report doesn't say to fix them."""
        # Print a report with only a warning
        report: str = _printed_report([Damage(Severity.WARNING, "a.md", "needs a look")])

        # Expect the totals without the fix line
        self.assertEqual(report, "warning a.md: needs a look\n\n0 errors, 1 warnings.\n")
