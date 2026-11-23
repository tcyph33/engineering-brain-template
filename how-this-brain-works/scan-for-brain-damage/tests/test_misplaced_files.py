"""Tests for finding files in places, or with names, the manual doesn't define."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.misplaced_files import find_misplaced_files
from damage import Damage, Severity
from scratch_brain import ScratchBrain

# Where the scan's own code lives.
SCAN_FOLDER: str = "how-this-brain-works/scan-for-brain-damage"


def _misplaced_files_in(test_case: unittest.TestCase, path: str) -> list[Damage]:
    """Finds misplaced files in a brain holding one file.

    Args:
        test_case: The test the brain is for.
        path: The one file's brain-relative path.

    Returns:
        What the check reports.
    """
    # Load a brain with only this file, and check it
    brain: Brain = ScratchBrain.load(test_case, {path: "text\n"})
    damage: list[Damage] = find_misplaced_files(brain)
    return damage


def _misplaced_file_damage(path: str) -> list[Damage]:
    """The damage reported for one misplaced file.

    Args:
        path: The file's brain-relative path.

    Returns:
        The one error the check gives it.
    """
    # Build the expected error
    MISPLACED_DESCRIPTION: str = (
        "isn't a place or file name the manual defines; see 'Where knowledge goes' "
        "(names are kebab-case)"
    )
    damage: list[Damage] = [Damage(Severity.ERROR, path, MISPLACED_DESCRIPTION)]
    return damage


class MisplacedNoteTest(unittest.TestCase):
    """Where notes may live, and how they're named."""

    def test_note_in_a_place_the_manual_defines_is_not_misplaced(self) -> None:
        """A dependency note in its project's dependencies/ folder has a place."""
        # Check a dependency note
        damage: list[Damage] = _misplaced_files_in(self, "projects/a/dependencies/a-thing.md")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_note_name_that_is_not_kebab_case_is_misplaced(self) -> None:
        """Note names are lowercase words joined by hyphens."""
        # Check a capitalized note name
        damage: list[Damage] = _misplaced_files_in(self, "principles/Big-Idea.md")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("principles/Big-Idea.md"))

    def test_note_name_with_accented_letters_is_misplaced(self) -> None:
        """Kebab-case names use only a-z, digits, and hyphens."""
        # Check an accented note name
        damage: list[Damage] = _misplaced_files_in(self, "principles/café.md")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("principles/café.md"))

    def test_note_in_a_folder_the_manual_does_not_define_is_misplaced(self) -> None:
        """Notes only go in the folders the manual names."""
        # Check a note in an extra folder
        damage: list[Damage] = _misplaced_files_in(self, "principles/more/idea.md")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("principles/more/idea.md"))


class MisplacedOtherFileTest(unittest.TestCase):
    """Where files that aren't notes may live."""

    def test_file_the_manual_does_not_define_is_misplaced(self) -> None:
        """A loose file at the root has no place."""
        # Check a stray text file
        damage: list[Damage] = _misplaced_files_in(self, "Notes.txt")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("Notes.txt"))

    def test_license_at_the_root_is_not_misplaced(self) -> None:
        """The brain's license lives at its root."""
        # Check a root license
        damage: list[Damage] = _misplaced_files_in(self, "LICENSE")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_license_in_a_folder_is_misplaced(self) -> None:
        """Only the root has a license."""
        # Check a license inside a folder
        damage: list[Damage] = _misplaced_files_in(self, "principles/LICENSE")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("principles/LICENSE"))

    def test_gitignore_at_the_root_is_not_misplaced(self) -> None:
        """The brain's .gitignore lives at its root."""
        # Check a root .gitignore
        damage: list[Damage] = _misplaced_files_in(self, ".gitignore")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_gitignore_in_a_folder_is_misplaced(self) -> None:
        """Only the root has a .gitignore."""
        # Check a .gitignore inside a folder
        damage: list[Damage] = _misplaced_files_in(self, "principles/.gitignore")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("principles/.gitignore"))

    def test_gitkeep_in_the_brains_lessons_folder_is_not_misplaced(self) -> None:
        """The brain's lessons-learned/ folder may be kept while empty."""
        # Check the brain's lessons placeholder
        damage: list[Damage] = _misplaced_files_in(self, "lessons-learned/.gitkeep")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_gitkeep_in_a_projects_lessons_folder_is_not_misplaced(self) -> None:
        """A project's lessons-learned/ folder may be kept while empty."""
        # Check a project's lessons placeholder
        damage: list[Damage] = _misplaced_files_in(self, "projects/a/lessons-learned/.gitkeep")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_gitkeep_outside_a_lessons_folder_is_misplaced(self) -> None:
        """Only lessons folders are kept while empty."""
        # Check a placeholder in another folder
        damage: list[Damage] = _misplaced_files_in(self, "principles/.gitkeep")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("principles/.gitkeep"))


class MisplacedScanFileTest(unittest.TestCase):
    """Where the scan's own files may live."""

    def test_scan_module_is_not_misplaced(self) -> None:
        """The scan's modules live in its folder."""
        # Check a scan module
        damage: list[Damage] = _misplaced_files_in(self, f"{SCAN_FOLDER}/__main__.py")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_scan_check_is_not_misplaced(self) -> None:
        """The scan's checks live in its checks/ folder."""
        # Check a scan check
        damage: list[Damage] = _misplaced_files_in(self, f"{SCAN_FOLDER}/checks/broken_links.py")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_scan_test_is_not_misplaced(self) -> None:
        """The scan's tests live in its tests/ folder."""
        # Check a scan test
        damage: list[Damage] = _misplaced_files_in(self, f"{SCAN_FOLDER}/tests/test_note.py")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_scan_file_with_digits_is_not_misplaced(self) -> None:
        """Snake_case names may hold digits."""
        # Check a test whose name has a digit
        damage: list[Damage] = _misplaced_files_in(self, f"{SCAN_FOLDER}/tests/test_utf8.py")

        # Expect nothing reported
        self.assertEqual(damage, [])

    def test_scan_file_with_capitals_is_misplaced(self) -> None:
        """The scan's Python files are named in snake_case."""
        # Check a capitalized Python file
        damage: list[Damage] = _misplaced_files_in(self, f"{SCAN_FOLDER}/Stray.py")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage(f"{SCAN_FOLDER}/Stray.py"))

    def test_scan_file_in_a_deeper_folder_is_misplaced(self) -> None:
        """The scan has no folders below checks/ and tests/."""
        # Check a Python file below checks/
        damage: list[Damage] = _misplaced_files_in(self, f"{SCAN_FOLDER}/checks/more/extra.py")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage(f"{SCAN_FOLDER}/checks/more/extra.py"))

    def test_other_file_in_the_scan_folder_is_misplaced(self) -> None:
        """The scan's folder holds only Python files."""
        # Check a text file in the scan's folder
        damage: list[Damage] = _misplaced_files_in(self, f"{SCAN_FOLDER}/notes.txt")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage(f"{SCAN_FOLDER}/notes.txt"))

    def test_python_file_outside_the_scan_folder_is_misplaced(self) -> None:
        """Code only lives in the scan's folder."""
        # Check a Python file elsewhere
        damage: list[Damage] = _misplaced_files_in(self, "principles/helper.py")

        # Expect it reported
        self.assertEqual(damage, _misplaced_file_damage("principles/helper.py"))
