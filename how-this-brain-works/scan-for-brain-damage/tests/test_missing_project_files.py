"""Tests for finding projects missing the files every project has."""

from __future__ import annotations

import unittest

from brain import Brain
from checks.missing_project_files import find_missing_project_files
from damage import Damage, Severity
from scratch_brain import ScratchBrain


class MissingProjectFilesTest(unittest.TestCase):
    """Which project files are required."""

    def test_project_without_its_readme_is_reported(self) -> None:
        """Every project has README.md."""
        # Load a brain with a project missing its README
        brain: Brain = ScratchBrain.load(self, {"projects/a/domain-concepts.md": "# A\n"})

        # Expect the README named
        self.assertEqual(find_missing_project_files(brain), [Damage(
            Severity.ERROR,
            "projects/a/",
            "every project has README.md, even if it's nearly empty",
        )])

    def test_project_without_its_domain_concepts_is_reported(self) -> None:
        """Every project has domain-concepts.md."""
        # Load a brain with a project missing its domain concepts
        brain: Brain = ScratchBrain.load(self, {"projects/a/README.md": "# A\n"})

        # Expect the domain concepts named
        self.assertEqual(find_missing_project_files(brain), [Damage(
            Severity.ERROR,
            "projects/a/",
            "every project has domain-concepts.md, even if it's nearly empty",
        )])

    def test_project_with_both_files_is_not_reported(self) -> None:
        """A project with its README and domain concepts is complete."""
        # Load a brain with a complete project
        brain: Brain = ScratchBrain.load(self, {
            "projects/a/README.md": "# A\n",
            "projects/a/domain-concepts.md": "# A domain concepts\n",
        })

        # Expect nothing reported
        self.assertEqual(find_missing_project_files(brain), [])
