"""Tests for checking pointers against GitHub, with a stand-in GitHub so they run offline."""

from __future__ import annotations

import unittest
from typing import cast

from brain import Brain
from checks.pointer_damage import find_pointer_damage
from damage import Damage, Severity
from github import GitHub
from note_with_frontmatter import note_with_frontmatter
from scratch_brain import ScratchBrain
from stand_in_github import UNREACHABLE_MESSAGE, StandInGitHub

# Where each test's note lives.
NOTE_PATH: str = "projects/a/dependencies/a-thing.md"
# The pointer's target, and its file's text when it exists.
TARGET: str = "owner/name/src/thing.py"
TARGET_TEXT: str = "class Thing:\n    pass\n"


def _pointer_damage(
    test_case: unittest.TestCase, github: StandInGitHub, *pointer_lines: str
) -> list[Damage]:
    """Checks a note's pointers against a stand-in GitHub.

    Args:
        test_case: The test the brain is for.
        github: The stand-in's fixed answers.
        pointer_lines: The lines under the note's pointers field.

    Returns:
        What the check reports.
    """
    # Load a brain whose one note has these pointers, and check them
    brain: Brain = ScratchBrain.load(
        test_case, {NOTE_PATH: note_with_frontmatter("pointers:", *pointer_lines)}
    )
    damage: list[Damage] = find_pointer_damage(brain, cast(GitHub, github))
    return damage


def _verified_pointer(verified_stamp: str) -> tuple[str, ...]:
    """The lines of a pointer to the target's Thing class, verified with the given stamp.

    Args:
        verified_stamp: The verified field's value.

    Returns:
        The pointer's lines.
    """
    # Write a full pointer
    pointer_lines: tuple[str, ...] = (
        "  - what: The thing",
        "    repo: owner/name",
        "    path: src/thing.py",
        "    symbol: Thing",
        f"    verified: {verified_stamp}",
    )
    return pointer_lines


class PointerTargetDamageTest(unittest.TestCase):
    """Whether a pointer's file and symbol are still there."""

    def test_pointer_to_a_file_not_on_github_is_reported(self) -> None:
        """A file that's gone, unpushed, or hidden is an error."""
        # Check a pointer whose file GitHub doesn't have
        damage: list[Damage] = _pointer_damage(
            self, StandInGitHub(files={}), *_verified_pointer("2026-11-22 @ a1b2c3d")
        )

        # Expect it reported
        self.assertEqual(damage, [Damage(
            Severity.ERROR,
            NOTE_PATH,
            f"pointer to The thing: {TARGET} isn't on GitHub, or your gh account can't see "
            "it; it was moved or deleted, hasn't been pushed, or is private",
        )])

    def test_pointer_whose_symbol_left_the_file_is_reported(self) -> None:
        """A file that no longer holds its symbol is an error."""
        # Check a pointer whose file lost the Thing class
        github: StandInGitHub = StandInGitHub(files={TARGET: "class Other:\n    pass\n"})
        damage: list[Damage] = _pointer_damage(
            self, github, *_verified_pointer("2026-11-22 @ a1b2c3d")
        )

        # Expect it reported
        self.assertEqual(damage, [Damage(
            Severity.ERROR, NOTE_PATH, f"pointer to The thing: Thing is no longer in {TARGET}"
        )])

    def test_pointer_whose_file_lookup_fails_is_warned_about(self) -> None:
        """A pointer GitHub couldn't be asked about needs a later look."""
        # Check a pointer whose lookup fails
        github: StandInGitHub = StandInGitHub(files={}, unreachable_files=frozenset({TARGET}))
        damage: list[Damage] = _pointer_damage(
            self, github, *_verified_pointer("2026-11-22 @ a1b2c3d")
        )

        # Expect a warning
        self.assertEqual(damage, [Damage(
            Severity.WARNING,
            NOTE_PATH,
            f"pointer to {TARGET} couldn't be checked: {UNREACHABLE_MESSAGE}",
        )])

    def test_web_pointer_is_not_checked(self) -> None:
        """Pointers to web pages aren't looked up."""
        # Check a web pointer against a GitHub with no files
        damage: list[Damage] = _pointer_damage(
            self, StandInGitHub(files={}), "  - what: A doc", "    url: https://example.com"
        )

        # Expect nothing reported
        self.assertEqual(damage, [])


class PointerChangeDamageTest(unittest.TestCase):
    """Whether a pointer's file changed since it was verified."""

    def test_unchanged_pointer_is_not_reported(self) -> None:
        """A file that's there, with its symbol, unchanged, is fine."""
        # Check a pointer to an unchanged file
        damage: list[Damage] = _pointer_damage(
            self, StandInGitHub(files={TARGET: TARGET_TEXT}), *_verified_pointer("2026-11-22")
        )

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_file_changed_since_its_verified_commit_is_warned_about(self) -> None:
        """A change after the verified commit means the note needs re-checking."""
        # Check a pointer whose file changed after its commit
        github: StandInGitHub = StandInGitHub(
            files={TARGET: TARGET_TEXT}, changed_targets=frozenset({TARGET})
        )
        damage: list[Damage] = _pointer_damage(
            self, github, *_verified_pointer("2026-11-22 @ a1b2c3d")
        )

        # Expect a warning naming the stamp
        self.assertEqual(damage, [Damage(
            Severity.WARNING,
            NOTE_PATH,
            f"{TARGET} changed since it was verified (2026-11-22 @ a1b2c3d); re-check the "
            "note and update verified",
        )])

    def test_file_changed_since_its_verified_date_is_warned_about(self) -> None:
        """Without a commit, a change after the verified date counts."""
        # Check a date-only pointer whose file changed
        github: StandInGitHub = StandInGitHub(
            files={TARGET: TARGET_TEXT}, changed_targets=frozenset({TARGET})
        )
        damage: list[Damage] = _pointer_damage(self, github, *_verified_pointer("2026-11-22"))

        # Expect a warning naming the stamp
        self.assertEqual(damage, [Damage(
            Severity.WARNING,
            NOTE_PATH,
            f"{TARGET} changed since it was verified (2026-11-22); re-check the note and "
            "update verified",
        )])

    def test_pointer_without_a_verified_stamp_is_warned_about(self) -> None:
        """With no stamp, there's nothing to compare against."""
        # Check a pointer with no verified field
        damage: list[Damage] = _pointer_damage(
            self,
            StandInGitHub(files={TARGET: TARGET_TEXT}),
            "  - repo: owner/name",
            "    path: src/thing.py",
        )

        # Expect a warning
        self.assertEqual(damage, [Damage(
            Severity.WARNING,
            NOTE_PATH,
            f"pointer to {TARGET} has no verified date; verify it and add one",
        )])

    def test_pointer_whose_history_lookup_fails_is_warned_about(self) -> None:
        """A change that couldn't be checked needs a later look."""
        # Check a pointer whose history lookup fails
        github: StandInGitHub = StandInGitHub(
            files={TARGET: TARGET_TEXT}, unreachable_histories=frozenset({TARGET})
        )
        damage: list[Damage] = _pointer_damage(self, github, *_verified_pointer("2026-11-22"))

        # Expect a warning
        self.assertEqual(damage, [Damage(
            Severity.WARNING,
            NOTE_PATH,
            f"couldn't tell whether {TARGET} changed: {UNREACHABLE_MESSAGE}",
        )])
