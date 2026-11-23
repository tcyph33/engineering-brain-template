"""StandInGitHub: answers the scan's questions about pointer targets from fixed answers, in
place of GitHub, so pointer tests run offline and always get the same answers."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional

from github import GitHubLookupError

# What a failed lookup says, as GitHub's would when it can't be reached.
UNREACHABLE_MESSAGE: str = "GitHub couldn't be reached"


@dataclass(frozen=True)
class StandInGitHub:
    """A GitHub whose files and history are fixed by the test.

    Targets are written "owner/name/path", as a pointer's target is.

    Attributes:
        files: Each existing file's text, by target.
        changed_targets: Targets that changed after any verified stamp.
        unreachable_files: Targets whose file lookup fails.
        unreachable_histories: Targets whose history lookup fails.
    """

    files: Mapping[str, str]
    changed_targets: frozenset[str] = field(default_factory=frozenset)
    unreachable_files: frozenset[str] = field(default_factory=frozenset)
    unreachable_histories: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        """Stores a read-only copy of the files, so no test's dict is shared."""
        # Copy and freeze the files
        object.__setattr__(self, "files", MappingProxyType(dict(self.files)))

    def file_text(self, repository: str, path: str) -> Optional[str]:
        """A file's text, as GitHub.file_text gives it.

        Args:
            repository: The repository, as "owner/name".
            path: The file's path in the repository.

        Returns:
            The file's text, or None when the file doesn't exist.

        Raises:
            GitHubLookupError: If the target is one whose file lookup fails.
        """
        # Fail for an unreachable target, otherwise answer from the fixed files
        target: str = f"{repository}/{path}"
        is_unreachable: bool = (target in self.unreachable_files)
        if is_unreachable:
            raise GitHubLookupError(UNREACHABLE_MESSAGE)
        found_text: Optional[str] = self.files.get(target)
        return found_text

    def has_file_changed_since_commit(self, repository: str, path: str, commit: str) -> bool:
        """Whether a file changed after a commit, as GitHub's method of the same name says.

        Args:
            repository: The repository, as "owner/name".
            path: The file's path in the repository.
            commit: The commit it was verified at; any commit gets the same answer.

        Returns:
            True when the target is one that changed.

        Raises:
            GitHubLookupError: If the target is one whose history lookup fails.
        """
        # Answer from the fixed history
        has_changed: bool = self._has_changed(f"{repository}/{path}")
        return has_changed

    def has_file_changed_since_date(self, repository: str, path: str, date: str) -> bool:
        """Whether a file changed after a date, as GitHub's method of the same name says.

        Args:
            repository: The repository, as "owner/name".
            path: The file's path in the repository.
            date: The day it was verified; any day gets the same answer.

        Returns:
            True when the target is one that changed.

        Raises:
            GitHubLookupError: If the target is one whose history lookup fails.
        """
        # Answer from the fixed history
        has_changed: bool = self._has_changed(f"{repository}/{path}")
        return has_changed

    def _has_changed(self, target: str) -> bool:
        """Whether a target changed, from the fixed history.

        Args:
            target: The target, as "owner/name/path".

        Returns:
            True when the target is one that changed.

        Raises:
            GitHubLookupError: If the target is one whose history lookup fails.
        """
        # Fail for an unreachable history, otherwise answer from the changed targets
        is_unreachable: bool = (target in self.unreachable_histories)
        if is_unreachable:
            raise GitHubLookupError(UNREACHABLE_MESSAGE)
        has_changed: bool = (target in self.changed_targets)
        return has_changed
