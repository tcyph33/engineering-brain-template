"""Tests for running the scan from the command line, end to end: a copy of the scan runs in
a scratch brain, as it does in a real one."""

from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from scratch_brain import FileContents, ScratchBrain

# Where the scan lives inside a brain.
SCAN_FOLDER_IN_BRAIN: str = "how-this-brain-works/scan-for-brain-damage"
# The files of the smallest brain that scans clean, beside the scan itself; it ignores what
# the real brain does, so files an editor or Python left in this scan's folder don't count.
CLEAN_BRAIN_FILES: Mapping[str, FileContents] = MappingProxyType({
    ".gitignore": "__pycache__/\n.DS_Store\n",
    "README.md": "# Brain\n\n@principles/README.md\n",
    "principles/README.md": "# Principles\n",
})


def _scratch_brain_with_scan(
    test_case: unittest.TestCase, files: Mapping[str, FileContents]
) -> ScratchBrain:
    """Builds a scratch brain from files and copies this scan, tests included, into it.

    Args:
        test_case: The test the brain is for; its cleanup removes the brain.
        files: The brain's files, besides the scan.

    Returns:
        The brain, with the scan in its place.

    Raises:
        subprocess.CalledProcessError: If git can't make the brain's repository.
        FileNotFoundError: If git isn't installed.
        shutil.Error: If the scan can't be copied.
    """
    # Build the brain, then copy this scan's folder in, leaving out any bytecode
    scratch_brain: ScratchBrain = ScratchBrain.create(test_case, files)
    scan_folder: Path = Path(__file__).resolve().parent.parent
    shutil.copytree(
        scan_folder,
        (scratch_brain.root / SCAN_FOLDER_IN_BRAIN),
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    return scratch_brain


def _run_scan(scratch_brain: ScratchBrain) -> subprocess.CompletedProcess[str]:
    """Runs the brain's copy of the scan from its root, without the GitHub checks.

    Args:
        scratch_brain: The brain to scan.

    Returns:
        The finished run, with its exit status and output.
    """
    # Run the scan as the manual says, writing no bytecode into the brain
    finished_run: subprocess.CompletedProcess[str] = subprocess.run(
        [sys.executable, "-B", SCAN_FOLDER_IN_BRAIN, "--skip-pointers"],
        cwd=scratch_brain.root,
        capture_output=True,
        text=True,
    )
    return finished_run


class CommandLineTest(unittest.TestCase):
    """The scan's exit status and output."""

    def test_clean_brain_exits_0_and_says_so(self) -> None:
        """A brain with nothing wrong, the scan's own files included, passes."""
        # Scan the smallest clean brain
        finished_run: subprocess.CompletedProcess[str] = _run_scan(
            _scratch_brain_with_scan(self, CLEAN_BRAIN_FILES)
        )

        # Expect a pass and the all-clear
        self.assertEqual(
            (finished_run.returncode, finished_run.stdout), (0, "No brain damage found.\n")
        )

    def test_damaged_brain_exits_1_and_lists_the_damage(self) -> None:
        """A brain with an error fails, and the report says what to fix."""
        # Scan a clean brain plus a stray file
        damaged_files: dict[str, FileContents] = dict(CLEAN_BRAIN_FILES)
        damaged_files["Notes.txt"] = "text"
        finished_run: subprocess.CompletedProcess[str] = _run_scan(
            _scratch_brain_with_scan(self, damaged_files)
        )

        # Expect a failure and the stray file reported
        self.assertEqual((finished_run.returncode, finished_run.stdout), (1, (
            "error   Notes.txt: isn't a place or file name the manual defines; see 'Where "
            "knowledge goes' (names are kebab-case)\n"
            "\n"
            "1 errors, 0 warnings.\n"
            "Fix the errors before committing.\n"
        )))

    def test_brain_that_is_not_a_git_repository_exits_2(self) -> None:
        """A brain git can't list can't be scanned, and the reason goes to stderr."""
        # Scan a clean brain whose repository was taken away
        scratch_brain: ScratchBrain = _scratch_brain_with_scan(self, CLEAN_BRAIN_FILES)
        shutil.rmtree(scratch_brain.root / ".git")
        finished_run: subprocess.CompletedProcess[str] = _run_scan(scratch_brain)

        # Expect the unreadable status and the reason
        self.assertEqual((finished_run.returncode, finished_run.stderr), (
            2,
            f"Can't scan the brain: {scratch_brain.root} isn't a git repository; the brain "
            "must be one\n",
        ))
