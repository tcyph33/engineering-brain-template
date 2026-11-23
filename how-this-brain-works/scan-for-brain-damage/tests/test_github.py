"""Tests for asking the real GitHub about pointer targets. Every test that calls GitHub is
marked @calls_real_github, and is skipped when the gh CLI isn't installed or signed in.

They ask about GitHub's own demo repository, octocat/Hello-World, which hasn't changed since
2012: its README was added in commit 553c207 and last changed in commit 7629413, on
2011-09-14.
"""

from __future__ import annotations

import unittest
from typing import Optional

from calls_real_github import calls_real_github
from github import GitHub, GitHubLookupError

# The repository asked about, and its one file.
REPOSITORY: str = "octocat/Hello-World"
README_PATH: str = "README"
# The commit that added the README, and the later one that last changed it.
README_ADDED_COMMIT: str = "553c2077f0edc3d5dc5d17262f6aa498e69d6f8e"
README_LAST_CHANGED_COMMIT: str = "762941318ee16e59dabbacb1b4049eec22f0d303"
# A repository that doesn't exist.
MISSING_REPOSITORY: str = "octocat/no-such-repository-for-brain-scan-tests"


class GitHubConnectionTest(unittest.TestCase):
    """Getting a connection, which needs no call to GitHub."""

    def test_connection_built_without_connect_is_refused(self) -> None:
        """Only GitHub.connect(), which checks gh first, can make a connection."""
        # Build a connection directly, and expect a refusal
        with self.assertRaisesRegex(
            TypeError, "^get a GitHub connection with GitHub.connect\\(\\)$"
        ):
            GitHub("gh", object())


class GitHubFileTextTest(unittest.TestCase):
    """Fetching a pointer's file from the real GitHub."""

    @calls_real_github
    def test_existing_file_text_is_fetched(self, github: GitHub) -> None:
        """A file on the default branch comes back as its text."""
        # Fetch the README
        file_text: Optional[str] = github.file_text(REPOSITORY, README_PATH)

        # Expect its text
        self.assertEqual(file_text, "Hello World!\n")

    @calls_real_github
    def test_missing_file_is_none(self, github: GitHub) -> None:
        """A file the repository doesn't have isn't an error, just absent."""
        # Fetch a file that isn't there
        file_text: Optional[str] = github.file_text(REPOSITORY, "no-such-file.md")

        # Expect nothing
        self.assertIsNone(file_text)

    @calls_real_github
    def test_file_in_a_missing_repository_is_none(self, github: GitHub) -> None:
        """A repository that doesn't exist, or can't be seen, holds no files."""
        # Fetch a file from a repository that isn't there
        file_text: Optional[str] = github.file_text(MISSING_REPOSITORY, README_PATH)

        # Expect nothing
        self.assertIsNone(file_text)

    @calls_real_github
    def test_folder_is_refused(self, github: GitHub) -> None:
        """A pointer must name a file, not a folder."""
        # Fetch the repository's root folder, and expect a refusal naming the problem
        with self.assertRaisesRegex(GitHubLookupError, "^the path is a folder; point at a file$"):
            github.file_text(REPOSITORY, "")


class GitHubChangeSinceCommitTest(unittest.TestCase):
    """Whether a file changed after a commit, on the real GitHub."""

    @calls_real_github
    def test_file_changed_after_an_earlier_commit(self, github: GitHub) -> None:
        """A change after the verified commit is found."""
        # Ask about the README since the commit that added it
        has_changed: bool = github.has_file_changed_since_commit(
            REPOSITORY, README_PATH, README_ADDED_COMMIT
        )

        # Expect the later change found
        self.assertTrue(has_changed)

    @calls_real_github
    def test_file_unchanged_since_its_last_change(self, github: GitHub) -> None:
        """Verified at the commit that last changed it, the file hasn't changed since."""
        # Ask about the README since its last change
        has_changed: bool = github.has_file_changed_since_commit(
            REPOSITORY, README_PATH, README_LAST_CHANGED_COMMIT
        )

        # Expect no change
        self.assertFalse(has_changed)

    @calls_real_github
    def test_unknown_commit_is_refused(self, github: GitHub) -> None:
        """A commit the repository doesn't have can't be compared."""
        # Ask about a commit that doesn't exist, and expect a refusal naming it
        with self.assertRaisesRegex(
            GitHubLookupError, f"^commit 0000000 isn't in {REPOSITORY}$"
        ):
            github.has_file_changed_since_commit(REPOSITORY, README_PATH, "0000000")

    @calls_real_github
    def test_missing_repository_is_refused(self, github: GitHub) -> None:
        """A repository that can't be read has no history to compare."""
        # Ask about a repository that doesn't exist, and expect a refusal naming it
        with self.assertRaisesRegex(
            GitHubLookupError, f"^{MISSING_REPOSITORY} doesn't exist or can't be read$"
        ):
            github.has_file_changed_since_commit(
                MISSING_REPOSITORY, README_PATH, README_ADDED_COMMIT
            )


class GitHubChangeSinceDateTest(unittest.TestCase):
    """Whether a file changed after a day, on the real GitHub."""

    @calls_real_github
    def test_file_changed_after_an_earlier_day(self, github: GitHub) -> None:
        """A change on a later day is found."""
        # Ask about the README since the day it was added
        has_changed: bool = github.has_file_changed_since_date(
            REPOSITORY, README_PATH, "2011-01-26"
        )

        # Expect the later change found
        self.assertTrue(has_changed)

    @calls_real_github
    def test_change_on_the_verified_day_does_not_count(self, github: GitHub) -> None:
        """A change the same day is taken to be the one that was verified."""
        # Ask about the README since the day of its last change
        has_changed: bool = github.has_file_changed_since_date(
            REPOSITORY, README_PATH, "2011-09-14"
        )

        # Expect no change
        self.assertFalse(has_changed)
