"""ScratchBrain: a small brain in a temporary git repository, built for one test and removed
when that test ends, whether it passed or failed."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Union, cast

from brain import Brain

# A file's contents: text, written as UTF-8 exactly as given, or raw bytes.
FileContents = Union[str, bytes]


@dataclass(frozen=True)
class ScratchBrain:
    """A brain folder holding only the files one test needs.

    Attributes:
        root: The brain's root folder, inside a temporary folder removed after the test.
    """

    root: Path

    @classmethod
    def create(
        cls, test_case: unittest.TestCase, files: Mapping[str, FileContents]
    ) -> ScratchBrain:
        """Builds a brain from files, in a git repository that's removed after the test.

        Args:
            test_case: The test the brain is for; its cleanup removes the brain.
            files: Each file's contents, by brain-relative path with forward slashes.

        Returns:
            The brain's folder.

        Raises:
            subprocess.CalledProcessError: If git can't make the repository.
            FileNotFoundError: If git isn't installed.
        """
        # Make the temporary folder and have the test remove it when it ends, passed or
        # failed; the cleanup is registered first, so nothing after it can leak the folder
        temporary_folder: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory(
            prefix="brain-scan-test-"
        )
        test_case.addCleanup(temporary_folder.cleanup)
        root: Path = Path(temporary_folder.name).resolve()

        # Make it a git repository, since the scan lists the brain's files through git
        subprocess.run(
            ["git", "init", "--quiet", str(root)], check=True, capture_output=True
        )

        # Write each file, with its folders, byte for byte
        relative_path: str
        for relative_path in files:
            file_contents: FileContents = files[relative_path]
            is_text: bool = (isinstance(file_contents, str))
            file_bytes: bytes
            if is_text:
                file_bytes = cast(str, file_contents).encode("utf-8")
            else:
                file_bytes = cast(bytes, file_contents)
            file_path: Path = (root / relative_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(file_bytes)

        # Hand back the finished brain's folder
        scratch_brain: ScratchBrain = cls(root=root)
        return scratch_brain

    @classmethod
    def load(cls, test_case: unittest.TestCase, files: Mapping[str, FileContents]) -> Brain:
        """Builds a brain from files and loads it, as the scan would.

        Args:
            test_case: The test the brain is for; its cleanup removes the brain.
            files: Each file's contents, by brain-relative path with forward slashes.

        Returns:
            The loaded brain.

        Raises:
            subprocess.CalledProcessError: If git can't make the repository.
            FileNotFoundError: If git isn't installed.
            BrainLoadError: If the brain's files can't be listed.
        """
        # Build the folder, then load it
        scratch_brain: ScratchBrain = cls.create(test_case, files)
        brain: Brain = Brain.load(scratch_brain.root)
        return brain
