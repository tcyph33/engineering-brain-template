"""Tests for loading the brain: which files it holds, as git sees them."""

from __future__ import annotations

import shutil
import unittest

from brain import Brain, BrainLoadError
from scratch_brain import ScratchBrain


class BrainLoadTest(unittest.TestCase):
    """Which files and notes a loaded brain holds."""

    def test_new_files_not_yet_added_to_git_are_included(self) -> None:
        """Files git hasn't been told about are still part of the brain."""
        # Load a brain whose files were never added
        brain: Brain = ScratchBrain.load(self, {"README.md": "# Brain\n", "LICENSE": "text"})

        # Expect both files
        self.assertEqual(brain.file_paths, frozenset({"README.md", "LICENSE"}))

    def test_ignored_files_are_left_out(self) -> None:
        """Files the brain's .gitignore names aren't part of it."""
        # Load a brain with an ignored file
        brain: Brain = ScratchBrain.load(
            self, {".gitignore": ".DS_Store\n", ".DS_Store": "junk", "README.md": "# Brain\n"}
        )

        # Expect the ignored file missing
        self.assertEqual(brain.file_paths, frozenset({".gitignore", "README.md"}))

    def test_only_markdown_files_are_read_as_notes(self) -> None:
        """Notes are the .md files; other files are only listed."""
        # Load a brain with a note and another file
        brain: Brain = ScratchBrain.load(self, {"README.md": "# Brain\n", "LICENSE": "text"})

        # Expect one note
        self.assertEqual(list(brain.notes), ["README.md"])

    def test_note_that_is_not_utf8_is_set_aside_as_unreadable(self) -> None:
        """A note in another encoding is recorded as unreadable, not read."""
        # Load a brain with a Latin-1 note
        brain: Brain = ScratchBrain.load(self, {"lessons-learned/a-lesson.md": b"caf\xe9\n"})

        # Expect it among the unreadable notes
        self.assertEqual(list(brain.unreadable_notes), ["lessons-learned/a-lesson.md"])

    def test_folder_that_is_not_a_git_repository_cannot_be_loaded(self) -> None:
        """The brain must be a git repository, since git lists its files."""
        # Build a brain, then take away its repository
        scratch_brain: ScratchBrain = ScratchBrain.create(self, {"README.md": "# Brain\n"})
        shutil.rmtree(scratch_brain.root / ".git")

        # Expect loading it to fail
        with self.assertRaises(BrainLoadError):
            Brain.load(scratch_brain.root)


class BrainPathTest(unittest.TestCase):
    """Whether paths are in the brain, and which projects it has."""

    def test_path_with_different_capitals_is_not_in_the_brain(self) -> None:
        """Paths compare case-sensitively, as on GitHub."""
        # Load a brain with one README
        brain: Brain = ScratchBrain.load(self, {"README.md": "# Brain\n"})

        # Expect the lowercase name missing
        self.assertFalse(brain.contains_path("readme.md"))

    def test_folder_holding_a_file_is_in_the_brain(self) -> None:
        """A folder counts when a file is somewhere inside it."""
        # Load a brain with a nested file
        brain: Brain = ScratchBrain.load(self, {"projects/a/README.md": "# A\n"})

        # Expect its outer folder found
        self.assertTrue(brain.contains_path("projects"))

    def test_root_is_in_the_brain(self) -> None:
        """'.' is the brain's own root."""
        # Load a brain with one file
        brain: Brain = ScratchBrain.load(self, {"README.md": "# Brain\n"})

        # Expect the root found
        self.assertTrue(brain.contains_path("."))

    def test_projects_are_the_folders_under_projects(self) -> None:
        """Each folder holding files under projects/ is a project."""
        # Load a brain with two projects and a stray file
        brain: Brain = ScratchBrain.load(self, {
            "projects/first/README.md": "# First\n",
            "projects/second/dependencies/thing.md": "# Thing\n",
            "projects/README.md": "# Projects\n",
        })

        # Expect the two project names
        self.assertEqual(brain.project_names(), frozenset({"first", "second"}))
